# Teste Técnico (Extração de informações em Faturas de Energia)

Para garantir o eficiente gerenciamento dos créditos de energia provenientes de usinas de energia renovável, é fundamental a extração precisa e automática de dados das notas fiscais de energia elétrica. Além disso, possuir conhecimento sobre faturas de energia elétrica é importante para o sucesso na gestão desses recursos.

Logo, é proposto dois testes como parte da avaliação dos conhecimentos técnicos e teóricos dos candidatos. Essa avaliação tem o objetivo de medir a compreensão do participante no contexto da extração de dados de notas fiscais e no entendimento básico de faturas de energia elétrica.

# Teste 1

Em busca pela eficiência na leitura de faturas, a equipe de desenvolvimento propõe a criação de uma rotina que, a partir de faturas de energia elétrica em formato de PDF, seja capaz de extrair importantes informações.

Nesta atividade, você deve editar o arquivo read.py e desenvolver uma rotina capaz de realizar a leitura da fatura fatura_cpfl.pdf em formato de PDF e retornar as seguintes informações:

- Titular da fatura (Nome e Documento)
- Endereço completo do titular da fatura
- Classificação da Instalação
- Número da instalação
- Valor a Pagar para a distribuidora
- Data de Vencimento
- Mês ao qual a fatura é referente
- Tarifa total com tributos
- Tarifa total Aneel
- Quantidade em kWh do Consumo da fatura
- Saldo em kWh acumulado na Instalação
- Somatório das quantidades das energias compensadas (injetadas)
- Somatório dos Valores Totais das Operações R$
- Contribuição de iluminação Pública
- Alíquotas do ICMS, PIS e COFINS em %
- Linha digitável para pagamento

Organize a saída e visualização das informações extraídas.

# Documentação do Teste 1

Eu fiz uma abordagem mista **OCR + Regex**, utilizando as bibliotecas pdf2image para conversão, pytesseract para reconhecimento de texto e opencv para pré-processamento de imagem.

O código funciona através de um sistema de prioridades: primeiro, ele tenta localizar os dados via Regex no texto bruto (o que garante resiliência contra erros de acentuação e variações de layout); caso não encontre, ele utiliza o OCR por coordenadas (regiões) como backup. Essa lógica híbrida permite extrair campos complexos, como o somatório de energias compensadas e a linha digitável do PIX, com alta precisão, mesmo quando o documento apresenta ruídos ou caracteres distorcidos.
O texto bruto era difícil de processar pois às vezes vinha uma "tabela" com difícil demarcação entre os headers como:

```bash
Lote Roteiro de leitura N°. Medidor PN Reservado ao Fisco
18 RO90-00000000 22115555001 986654521

```
E eu demarquei as regiões em que os campos aparecem. Idealmente, eu poderia até comparar os dois se geraram o mesmo resultado, e escolhi o Regex como prioridade acima do OCR (isso foi arbitrário, o Regex pode dar errado e o OCR dar certo). O OCR também falha às vezes, lendo um "G" no lugar de "Ç".

Estou usando WSL. Eu também usei um ambiente virtual para facilitar instalar as libs, mas ele está no gitignore.

Como Executar o Projeto:

1. **Pré-requisitos**: Certifique-se de ter o Python 3.x instalado e as dependências do sistema (Tesseract OCR e Poppler para o pdf2image).
   - No Ubuntu/WSL: `sudo apt install tesseract-ocr poppler-utils`
2. **Instalação**: Instale as bibliotecas Python necessárias:

```bash
pip install -r requirements.txt
```
Para rodar o script, basta chamar `python read.py TIPO`, TIPO pode ser `cemig` ou `cpfl` Os outputs foram:

``` bash
gio@DESKTOP-C5DAE4V:~/teste-processamento-inteligente-de-documentos-19022026$ python read.py cemig
--- DADOS EXTRAÍDOS (CEMIG) ---
Titular Nome             : J OAO NEVES
Titular Documento        : 715.665.976-13
Titular Endereco Rua     : PCA DOUTOR GONCALVES 379 CS 802
Titular Endereco Bairro  : CENTRO
Titular Endereco Cep     : 35570-000 VICOSA, MG
Classificacao Instalacao : Residencial
Numero Instalacao        : 4547896527
Valor A Pagar            : R$76,66
Data Vencimento          : 06/08/2023
Mes Referencia           : | UL/2023
Tarifa Total Com Tributos: 0,95954601
Consumo Kwh              : 199 kWh
Linha Digitavel          : 1221111178789
Soma Energias Comp. R$   : -72.48
gio@DESKTOP-C5DAE4V:~/teste-processamento-inteligente-de-documentos-19022026$ python read.py cpfl
--- DADOS EXTRAÍDOS (CPFL) ---
Titular Nome             : JOAO NEVES
Titular Documento        : 715.665.976-13
Titular Endereco Rua     : PCA DOUTOR GONCALVES 379 CS 802
Titular Endereco Bairro  : CENTRO
Titular Endereco Cep     : 35570-000 VICOSA MG
Classificacao Instalacao : Convencional B1 Residencial - Bifasico 220 /127 V
Numero Instalacao        : 12385675
Valor A Pagar            : 219,14
Data Vencimento          : 28/11/2023
Mes Referencia           : OUT/2023
Tarifa Total Com Tributos: 0,47425000
Tarifa Aneel Te          : 0,31884000
Tarifa Aneel Tusd        : 0,37162000
Consumo Kwh              : 2000 kWh
Saldo Geracao Acumulado  : 0.0000000000 kWh kWh
Linha Digitavel          : 000700000026 122201111122 1234285129034 100735547711
gio@DESKTOP-C5DAE4V:~/teste-processamento-inteligente-de-documentos-19022026$ 

```
Mes Referencia           : | UL/2023
Aqui houve um erro do OCR, uma '|' ao invés de 'J', formando a palavra JUL. Também é importante entender que a data pode estar em vários formatos: Jul, Julho, 7, etc, e isso teria que ser padronizado.

Devido ao tempo de desenvolvimento, priorizei os campos de identificação, valores financeiros e consumo. Campos de tributação detalhada (Alíquotas ICMS/PIS/COFINS) e somatórios de operações específicas estão mapeados na estrutura do código, mas requerem ajustes de Regex adicionais para plena captura nos diferentes layouts.

# Teste 2

Contexto: Você recebeu a fatura "fatura_cemig.pdf" e deve desenvolver um script para extrair seus dados. Antes de iniciar a programação, é essencial compreender e interpretar as informações presentes nesta fatura.

Atividade: Analise a fatura e redija um documento respondendo os pontos abaixo. As respostas podem ser inseridas neste 'README'.

 - Identifique as principais diferenças entre a fatura "fatura_cemig.pdf" e uma fatura convencional de energia elétrica "fatura_cemig_convencional.pdf".
 - Descreva e explique os termos e valores apresentados na seção "Valores Faturados" da fatura "fatura_cemig.pdf".
 - Considerando que a instalação da "fatura_cemig.pdf" participa do Sistema de Compensação de Energia Elétrica, identifique e explique qual informação na seção "Informações Gerais" da fatura é considerada a mais importante.
 - Identifique o consumo da instalação referente ao mês de julho de 2023.

# Resposta para o Teste 2
    
    Resposta1: a fatura convencional tem alguns dados a mais como a chave de acesso e o link. Além disso os dados dentro das "caixas" mudam entre uma fatura e outra, o que dificulta a demarcação de regiões para o OCR, como por exemplo, na caixa "informações gerais".

    Resposta2: Esse bloco é crucial, pois detalha quanto foi injetado, quanto foi usado, tarifas, TE e TUSD, etc.

    Resposta3: SALDO ATUAL DE GERAÇÃO: 234,63 kWh., pois diz respeito a quanta energia você produziu e enviou para a distribuidora, e ela fará os descontos e cálculos de saldo, etc. 

    Resposta4: O consumo faturado na instalação em julho de 2023 foi de 199 kWh. A diferença em relação à fatura convencional (253 kWh) eu supónho que deve-se ao abatimento da energia injetada pelo sistema de microgeração, restando apenas o consumo líquido a ser pago à distribuidora


# Requisitos dos Desafios:

1. Utilize a linguagem Python para desenvolver a solução.
2. No mesmo README, inclua uma seção detalhada que explique claramente os passos necessários para executar o código. Certifique-se de que as instruções sejam precisas, organizadas e fáceis de entender, pois os avaliadores seguirão essa documentação.
3. Faça um fork do repositório, para iniciar o desenvolvimento.
4. A entrega deve ser realizada por meio de um pull request para o repositório original. Caso não consiga, os arquivos podem ser enviados para o email falecom@dg.energy, porém com penalidade de pontos.
5. Abra o pull request também faltando 5 minutos para o prazo final da entrega do teste. Se o pull request for realizado antes dos 5 minutos restantes haverá eliminação do candidato.
6. A entrega deve ser realizada até às 12:30h.
