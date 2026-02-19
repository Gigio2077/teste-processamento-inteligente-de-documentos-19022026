import cv2
import pytesseract
import numpy as np
from pdf2image import convert_from_path
import re
import sys

# --- CONFIGURAÇÃO DE PERFIS ---
perfis = {
    'cemig': {
        'arquivo': 'fatura_cemig.pdf',
        'regioes': {
            'titular_nome': (60, 220, 973, 268), 
            'titular_documento': (63, 380, 480, 417),  
            'titular_endereco_rua': (64, 271, 697, 304),
            'titular_endereco_bairro': (64, 305, 280, 334),
            'titular_endereco_cep': (64, 343, 464, 377),
            'classificacao_instalacao': (255, 757, 578, 830),
            'numero_instalacao': (1060, 3125, 1372, 3182),
            'valor_a_pagar': (1855, 3129, 2257, 3184),
            'data_vencimento': (1423, 3127, 1740, 3180),
            'mes_referencia': (1025, 252, 1321, 316),
            'tarifa_total_com_tributos': (1056, 1011, 1234, 1043),
            'consumo_kwh': (2234, 1887, 2336, 1927),
            'linha_digitavel': (614, 3131, 968, 3173),
        },
        'regex': {
            'titular_documento': r"(\d{3}\.\d{3}\.\d{3}-\d{2})",
            'classificacao_instalacao': r"CLASSIFICA..O:\s*(.*)",
            'saldo_geracao_acumulado': r"SALDO ATUAL DE GERA..O:\s*([\d,]+)",
            'contribuicao_iluminacao_publica': r"Contrib.*Ilum.*Publica.*\s+([\d,]+)",
        }
    },
    'cpfl': {
        'arquivo': 'fatura_cpfl.pdf',
        'regioes': {
            'titular_nome': (306, 315, 609, 353), 
            'titular_documento': (63, 380, 480, 417),  
            'titular_endereco_rua': (205, 1045, 752, 1068),
            'titular_endereco_bairro': (205, 1071, 643, 1094),
            'titular_endereco_cep': (205, 1093, 639, 1123),
            'classificacao_instalacao': (1462, 1045, 2075, 1073),
            'numero_instalacao': (906, 1244, 1094, 1291),
            'valor_a_pagar': (1758, 2979, 1923, 3019),
            'data_vencimento': (2084, 2982, 2280, 3017),
            'mes_referencia': (1241, 1206, 1456, 1278),
            'tarifa_total_com_tributos': (1091, 1446, 1209, 1473),
            'tarifa_aneel_te': (1103, 2050, 1212, 2069),
            'tarifa_aneel_tusd': (970, 2049, 1077, 2071),
            'consumo_kwh': (655, 2017, 722, 2040),
            'saldo_geracao_acumulado': (511, 2492, 728, 2514), # aqui eu usei "Saldo a expirar próximo mes"
            'linha_digitavel': (406, 3222, 1435, 3256),
        },
        'regex': {
            'energia_compensada_gd_ii': r"Energ.*Atv.*Inj.*TUSD.*?([\d,.]+)\s*kWh",
            'energia_compensada_adicional': r"Energ.*Atv.*Inj.*TE.*?([\d,.]+)\s*kWh",
            'linha_digitavel': r"PIX\s*([\d\s]{40,})\s*Autentica..o",
            'titular_documento': r"(\d{3}\.\d{3}\.\d{3}-\d{2})",

        }
    }
}

# Escolha do perfil (Pode mudar para 'cemig' para testar a outra)
# --- LÓGICA DE LINHA DE COMANDO ---
if len(sys.argv) < 2:
    print("Uso: python read.py [cemig|cpfl]")
    sys.exit(1)

perfil_atual = sys.argv[1].lower()

if perfil_atual not in perfis:
    print(f"Perfil '{perfil_atual}' não encontrado. Escolha entre: {', '.join(perfis.keys())}")
    sys.exit(1)

config = perfis[perfil_atual]

# 1. Converter PDF para Imagem
pages = convert_from_path(config['arquivo'], 300)
img = np.array(pages[0])

# Extração de texto bruto
texto_completo = pytesseract.image_to_string(img)

def extrair_campo_ocr(imagem, x1, y1, x2, y2):
    if not (x1 or y1 or x2 or y2): return None
    recorte = imagem[y1:y2, x1:x2]
    gray = cv2.cvtColor(recorte, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    res = pytesseract.image_to_string(thresh, config='--psm 7').strip()
    return res if res else None

# 4. Execução (Regex Primeiro -> OCR depois)
print(f"--- DADOS EXTRAÍDOS ({perfil_atual.upper()}) ---")

regioes = config['regioes']
regex_equivalentes = config['regex']

for campo in regioes.keys():
    resultado = None
    if campo in regex_equivalentes:
        match = re.search(regex_equivalentes[campo], texto_completo, re.IGNORECASE)
        if match:
            resultado = match.group(1).strip()
    
    if not resultado and regioes[campo]:
        resultado = extrair_campo_ocr(img, *regioes[campo])
    
    if resultado:
        nome_exibicao = campo.replace('_', ' ').title()
        unidade = " kWh" if "geracao" in campo or "consumo" in campo else ""
        print(f"{nome_exibicao:25}: {resultado}{unidade}")

# --- Lógica Especial para Somatórios ---
comp_gd2 = re.search(r"Energia compensada GD II.*?(-[\d,]+)", texto_completo)
comp_adic = re.search(r"Energia comp.\s+adicional.*?(-[\d,]+)", texto_completo, re.IGNORECASE)

if comp_gd2 or comp_adic:
    v1 = float(comp_gd2.group(1).replace(',', '.')) if comp_gd2 else 0.0
    v2 = float(comp_adic.group(1).replace(',', '.')) if comp_adic else 0.0
    print(f"{'Soma Energias Comp. R$':25}: {v1 + v2:.2f}")