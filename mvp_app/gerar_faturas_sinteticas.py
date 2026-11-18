from PIL import Image, ImageDraw, ImageFont
import json, os
os.makedirs("faturas_teste", exist_ok=True)
try:
    ft, fb, fs = ImageFont.load_default(size=28), ImageFont.load_default(size=22), ImageFont.load_default(size=18)
except TypeError:
    ft = fb = fs = ImageFont.load_default()
faturas = [
    {"arq": "faturas_teste/fatura_enel_sintetica.png", "emp": "ENEL DISTRIBUICAO SAO PAULO S.A.", "sede": "Sede Corporativa: Av. das Nacoes Unidas, 14401 - Barueri/SP", "cli": "LUCAS DE FREITAS PAGUNG (RM 553242 - DADO SINTETICO)", "end": "ENDERECO: RUA GENERAL FRANCISCO GLICERIO, 1020", "bai": "BAIRRO: CENTRO - SUZANO/SP", "cep": "CEP: 08674-000"},
    {"arq": "faturas_teste/fatura_sabesp_sintetica.png", "emp": "SABESP - CIA DE SANEAMENTO BASICO", "sede": "Sede Corporativa: Rua Costa Carvalho, 300 - Pinheiros/SP", "cli": "JOSE CARLOS PEREIRA (DADO SINTETICO)", "end": "ENDERECO: AVENIDA ANTONIO MARQUES FIGUEIRA, 450", "bai": "BAIRRO: VILA FIGUEIRA - SUZANO/SP", "cep": "CEP: 08676-000"},
    {"arq": "faturas_teste/fatura_claro_sintetica.png", "emp": "CLARO S.A. TELECOMUNICACOES", "sede": "Sede Corporativa: Rua Henri Dunant, 780 - Santo Amaro/SP", "cli": "ANA PAULA SOUZA (DADO SINTETICO)", "end": "ENDERECO: RUA BENJAMIN CONSTANT, 890", "bai": "BAIRRO: CENTRO - SUZANO/SP", "cep": "CEP: 08674-010"},
]
gab = {}
for f in faturas:
    img = Image.new("RGB", (1100, 560), (255, 255, 255))
    d = ImageDraw.Draw(img)
    d.rectangle([25, 25, 1075, 535], outline=(0, 0, 0), width=4)
    d.text((50, 50), f["emp"], fill=(0, 0, 0), font=ft); d.text((50, 95), f["sede"], fill=(80, 80, 80), font=fs)
    d.line([50, 135, 1050, 135], fill=(0, 0, 0), width=2)
    d.text((50, 165), f"TITULAR: {f['cli']}", fill=(0, 0, 0), font=fb); d.text((50, 220), f["end"], fill=(0, 0, 0), font=fb)
    d.text((50, 275), f["bai"], fill=(0, 0, 0), font=fb); d.text((50, 330), f["cep"], fill=(0, 0, 0), font=fb)
    img.save(f["arq"])
    gab[f["arq"]] = {"empresa": f["emp"].split()[0], "endereco_esperado": f["end"].replace("ENDERECO: ", ""), "cep_esperado": f["cep"].replace("CEP: ", "")}
json.dump(gab, open("faturas_teste/gabarito.json", "w", encoding="utf-8"), indent=2, ensure_ascii=False)
print("Faturas geradas!")
