import cv2, numpy as np, pytesseract, re
from PIL import Image


def corrigir_perspectiva_e_preprocessar(imagem_pil: Image.Image):
    img = np.array(imagem_pil.convert("RGB"))
    gray = cv2.cvtColor(cv2.cvtColor(img, cv2.COLOR_RGB2BGR), cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(cv2.GaussianBlur(gray, (5, 5), 0), 50, 150)
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    doc_cnt, max_area = None, 0
    for c in contours:
        area = cv2.contourArea(c)
        if area > 10000:
            approx = cv2.approxPolyDP(c, 0.02 * cv2.arcLength(c, True), True)
            if len(approx) == 4 and area > max_area:
                max_area, doc_cnt = area, approx
    if doc_cnt is not None:
        pts = doc_cnt.reshape(4, 2)
        rect = np.zeros((4, 2), dtype="float32")
        s, diff = pts.sum(axis=1), np.diff(pts, axis=1)
        rect[0], rect[2], rect[1], rect[3] = (
            pts[np.argmin(s)],
            pts[np.argmax(s)],
            pts[np.argmin(diff)],
            pts[np.argmax(diff)],
        )
        (tl, tr, br, bl) = rect
        w = max(int(np.linalg.norm(br - bl)), int(np.linalg.norm(tr - tl)))
        h = max(int(np.linalg.norm(tr - br)), int(np.linalg.norm(tl - bl)))
        dst = np.array([[0, 0], [w - 1, 0], [w - 1, h - 1], [0, h - 1]], dtype="float32")
        warped = cv2.warpPerspective(gray, cv2.getPerspectiveTransform(rect, dst), (w, h))
    else:
        warped = gray

    h_w, w_w = warped.shape[:2]
    if w_w < 1800:
        escala = min(3.0, max(2.0, 2000.0 / max(w_w, 1)))
        warped = cv2.resize(warped, None, fx=escala, fy=escala, interpolation=cv2.INTER_CUBIC)

    _, thresh = cv2.threshold(warped, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    thresh = cv2.copyMakeBorder(thresh, 20, 20, 20, 20, cv2.BORDER_CONSTANT, value=255)
    return thresh


def _extrair_cep(texto: str) -> str:
    m_label = re.search(r"CEP[:\s\-]*([0-9OoIl|BbSsZz\-\.\s–—]{8,14})", texto, re.IGNORECASE)
    if m_label:
        bruto = m_label.group(1).translate(str.maketrans("OoIl|BbSsZz", "00111885522"))
        digitos = re.sub(r"\D", "", bruto)
        if len(digitos) >= 8:
            return f"{digitos[:5]}-{digitos[5:8]}"

    m_cep = re.search(r"\b(\d{5})[\s\-\.–—]?(\d{3})\b", texto)
    if m_cep:
        return f"{m_cep.group(1)}-{m_cep.group(2)}"

    return ""


def extrair_dados_fatura(imagem_pil: Image.Image) -> dict:
    proc = corrigir_perspectiva_e_preprocessar(imagem_pil)
    try:
        texto_bruto = pytesseract.image_to_string(proc, lang="por", config="--psm 6")
    except Exception:
        texto_bruto = pytesseract.image_to_string(proc, config="--psm 6")

    tu = texto_bruto.upper()
    empresa = (
        "Enel Distribuição"
        if "ENEL" in tu
        else (
            "Sabesp Saneamento"
            if "SABESP" in tu
            else ("Claro Telecomunicações" if "CLARO" in tu else "Não identificada")
        )
    )
    corps = ["BARUERI", "COSTA CARVALHO", "RUA HENRI DUNANT", "CNPJ", "SEDE CORPORATIVA"]
    filtrado = "\n".join(
        [l.strip() for l in texto_bruto.splitlines() if l.strip() and not any(c in l.upper() for c in corps)]
    )
    m_rua = re.search(
        r"(?:ENDERE[CÇ]O(?:\s+DO\s+CLIENTE)?|LOCAL\s+DE\s+ENTREGA)?[:\s]*((?:RUA|AV\.?|AVENIDA|TRAVESSA|ALAMEDA|ESTRADA)\s+[A-ZÀ-Ú0-9\s,.-]+?(?:N[º°.]?\s*)?\d{1,5})",
        filtrado,
        re.IGNORECASE,
    )
    m_bairro = re.search(r"BAIRRO[:\s]*([^\n]+)", filtrado, re.IGNORECASE)
    cep = _extrair_cep(filtrado) or _extrair_cep(texto_bruto)

    return {
        "empresa_detectada": empresa,
        "logradouro": m_rua.group(1).strip() if m_rua else "",
        "cep": cep,
        "bairro_cidade": m_bairro.group(1).strip() if m_bairro else "",
        "texto_ocr_bruto": texto_bruto,
    }
