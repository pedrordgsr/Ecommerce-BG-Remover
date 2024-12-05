import os
import io
from tkinter import Tk, Label, Button, filedialog, messagebox
from rembg import remove
from PIL import Image, ImageFilter

def select_input_folder():
    folder = filedialog.askdirectory()
    if folder:
        input_folder_label.config(text=f"Entrada: {folder}")
        global input_folder
        input_folder = folder

def select_output_folder():
    folder = filedialog.askdirectory()
    if folder:
        output_folder_label.config(text=f"Saída: {folder}")
        global output_folder
        output_folder = folder

def process_images():
    if not input_folder or not output_folder:
        messagebox.showerror("Erro", "Por favor, selecione as pastas de entrada e saída!")
        return

    try:
        files = os.listdir(input_folder)
        images = [f for f in files if f.lower().endswith(('.png', '.jpg', '.jpeg'))]

        if not images:
            messagebox.showinfo("Aviso", "Nenhuma imagem encontrada na pasta de entrada!")
            return

        for image_file in images:
            input_path = os.path.join(input_folder, image_file)
            output_path = os.path.join(output_folder, os.path.splitext(image_file)[0] + "_processed.jpg")

            # Remove o fundo
            with open(input_path, 'rb') as input_file:
                input_image = input_file.read()
            output_image = remove(input_image)

            # Abre a imagem com o PIL para processamento adicional
            image = Image.open(io.BytesIO(output_image)).convert("RGBA")

            # Aplica um limiar de transparência para remover suavizações nas bordas
            threshold = 128  # Valor do limiar
            alpha = image.split()[3]  # Extrai o canal alpha
            alpha = alpha.point(lambda p: 255 if p > threshold else 0)  # Binariza o canal alpha
            image.putalpha(alpha)  # Aplica o canal alpha binarizado à imagem

            # Suavização nas bordas
            alpha = alpha.filter(ImageFilter.GaussianBlur(5))  # Suaviza as bordas com um desfoque
            image.putalpha(alpha)

            # Recorta a imagem ao conteúdo (elimina espaços vazios)
            bbox = image.getbbox()
            if bbox:
                contraction = 10  # Pixels para reduzir em cada lado
                x0, y0, x1, y1 = bbox
                x0 = max(x0 + contraction, 0)
                y0 = max(y0 + contraction, 0)
                x1 = min(x1 - contraction, image.width)
                y1 = min(y1 - contraction, image.height)
                bbox = (x0, y0, x1, y1)

                image_cropped = image.crop(bbox)
            else:
                image_cropped = image  # Caso bbox seja None, usa a imagem inteira

            # Redimensiona a imagem para caber dentro de 1200x1200 com margem de segurança
            margin = 50  # Pixels de margem de segurança
            target_size = 1200 - 2 * margin
            image_cropped.thumbnail((target_size, target_size), Image.LANCZOS)

            # Cria um fundo branco de 1200x1200
            final_image = Image.new("RGB", (1200, 1200), (255, 255, 255))

            # Calcula os offsets para centralizar a imagem com a margem
            offset_x = (1200 - image_cropped.width) // 2
            offset_y = (1200 - image_cropped.height) // 2

            # Cola a imagem redimensionada no fundo branco
            final_image.paste(image_cropped, (offset_x, offset_y), mask=image_cropped)

            # Salva a imagem final
            final_image.save(output_path, "JPEG")

        messagebox.showinfo("Sucesso", "Todas as imagens foram processadas com sucesso!")

    except Exception as e:
        messagebox.showerror("Erro", f"Ocorreu um erro: {e}")

# Inicializa as variáveis globais
input_folder = None
output_folder = None

# Cria a interface gráfica
root = Tk()
root.title("Removedor de Fundo de Imagens")

# Labels
Label(root, text="Selecione a pasta de entrada com as imagens:").pack(pady=5)
input_folder_label = Label(root, text="Nenhuma pasta selecionada", fg="gray")
input_folder_label.pack(pady=5)

Label(root, text="Selecione a pasta de saída para salvar as imagens:").pack(pady=5)
output_folder_label = Label(root, text="Nenhuma pasta selecionada", fg="gray")
output_folder_label.pack(pady=5)

# Botões
Button(root, text="Selecionar Pasta de Entrada", command=select_input_folder).pack(pady=5)
Button(root, text="Selecionar Pasta de Saída", command=select_output_folder).pack(pady=5)
Button(root, text="Processar Imagens", command=process_images, bg="green", fg="white").pack(pady=20)

# Executa a interface gráfica
root.mainloop()
