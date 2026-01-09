from flask import Flask,redirect,render_template,request,url_for,send_from_directory
import os
from werkzeug.utils import secure_filename
from pathlib import Path
from PyPDF2 import PdfMerger

SELF_PATH = Path(__file__).resolve().parent
print(SELF_PATH)

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = f'{SELF_PATH}\\uploads'

"""
O caminho da lógica do programa:
1. Rota '/', na função index
2. Rota '/upload', automaticamente redirecionado a '/download'
3. Rota '/download' pega a rota '/getpdf' e por fim fornece o arquivo
"""

"""
Possiveis erros:
1. Digamos que você coloca arquivos inválidos, o merger não vai falhar, porém como não hávera nenhum PDF no download, o sistema como um todo vai falhar

Solução 1: "Primeiro, após o cliente colocar todos os arquivos, o sistema vai verificar se tem dois ou mais arquivos PDFs. Se não, ele redireciona para uma tela de Erro".
Solução 2: "Se não houver nenhum arquivo na pasta downloads, ao invés do caminho normal, ai sim vem a página de erro"

2. Se o download do arquivo for o arquivo da pasta downloads, então, automaticamente esse site não pode ter mais de dois acessos. Até porque só há uma pasta uploads e uma pasta downloads

Solução 1: "Reestruturar o site para multicompatibilidade, refazendo o sistema de pastas usando tokens na URL"
Solução 2: "Criar um sistema de filas, onde o primeiro usuário pega o arquivo 1, o segundo usuário pega o arquivo 2, e assim por diante"

"""








def gen_app():
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.mkdir(app.config['UPLOAD_FOLDER'])
    
    if not os.path.exists(f'{SELF_PATH}\\download'):
        os.mkdir(f'{SELF_PATH}\\download')

    if not os.path.exists(f'{SELF_PATH}\\templates'):
        print("Sorry, I can't work. The 'templates' folder was not found")
        return False

    return True





def clear_uploads():
    for i in os.listdir(app.config["UPLOAD_FOLDER"]):
        os.remove(f'{app.config["UPLOAD_FOLDER"]}\\{i}')








def merge_all_pdfs():

    merger = PdfMerger()
    for nome in os.listdir(app.config['UPLOAD_FOLDER']):
        if nome.lower().endswith('.pdf'): merger.append(f'{app.config['UPLOAD_FOLDER']}\\{nome}')


    with open(f'{SELF_PATH}\\download\\PDF_Fundido.pdf','wb') as output:
        merger.write(output)

    merger.close()

    clear_uploads()












@app.route('/')
def index():
    return render_template('index.html')




@app.route('/error')
def error():
    error_n = request.args.get('error_n',500)
    desc = request.args.get('desc','Erro não listado')
    return render_template('error_page.html', error = error_n, desc = desc)






@app.route('/getpdf')
def get_pdf():
    if not os.listdir(f'{SELF_PATH}\\download') == []:
        return send_from_directory(f'{SELF_PATH}\\download','PDF_Fundido.pdf', as_attachment=True)
    else:
        return redirect(url_for('error', error_n = 404, desc = 'Seu arquivo PDF fundido não foi criado.'))









@app.route('/download')
def download():
    return render_template('download.html')









@app.route('/upload', methods=['POST'])
def upload_file():
    # No Flask, para múltiplos arquivos com o mesmo nome no form, use getlist
    files = request.files.getlist('arquivos[]')
    
    for file in files:
        if file.filename == '':
            continue
        if file:
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

    #Verificação de PDFs
    pdf_verificator = []
    for i in os.listdir(app.config['UPLOAD_FOLDER']):
        if i.endswith('.pdf'): pdf_verificator.append(True)
    
    if pdf_verificator == []:
        print("Upload files were deleted due to 'invalid data'")
        clear_uploads()
        return redirect(url_for('error', error_n = 400, desc = 'Não houve nenhum arquivo PDF'))

    merge_all_pdfs()
    
    # Redireciona para a página de download após terminar

    return redirect(url_for('download'))










if __name__ == "__main__":
    if gen_app(): app.run()