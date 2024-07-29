from seleniumbase import SB
from selenium.webdriver.common.by import By
import time
from selenium.webdriver.common.action_chains import ActionChains
from seleniumbase.common.exceptions import NoSuchElementException
from seleniumbase.common.exceptions import ElementNotVisibleException
import os
from PIL import Image
import dotenv
import pickle

dotenv.load_dotenv()

def aceptar_cookies(sb): 
    # accept cookies 
    try: 
        sb.click("button#CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll")
    except NoSuchElementException: 
        print('No cookies to accept')
    except ElementNotVisibleException: 
        print('No cookies to accept')

def obtener_link(sb): 
    # botón de "play all slides"
    sb.wait_for_element_clickable('div.play-all')
    sb.click('div.play-all')
    
    # espera a que botón de descargar esté disponible
    sb.wait_for_element_clickable("div#fullVideoModal div div:nth-of-type(2) button", timeout=150)

    # cuando aparezca el botón de descargar, cerrar la pantalla para obtener el link
    sb.click('//*[@id="fullVideoModal"]/div/div/button')

    # esperar a descargar
    sb.wait_for_element_clickable('span.export-element', timeout=300)
    sb.click('span.export-element')
    sb.click('//*[@id="container"]/div/div[1]/div[2]/div[1]/div[3]/div[2]/div/div[2]/div[3]/div[1]/button')
    link_to_video = sb.get_text('input#shareURLInput')
    return link_to_video

def save_cookies(driver): 
    # get cookies from driver
    print('Saving cookies')
    cookies = driver.driver.get_cookies()
  
    pickle.dump(cookies, open('cookies.pkl', 'wb'))

def load_cookies(sb):
    try:
        print('Adding cookies')
        cookies = pickle.load(open('cookies.pkl', 'rb'))
        for cookie in cookies:
            # Ensure domain is correctly set
            cookie['domain'] = 'placeit.net'
            if 'expiry' in cookie:
                del cookie['expiry']  # Selenium does not accept 'expiry' in this format
            print(cookie)
            try:
                sb.driver.add_cookie(cookie)
            except Exception as e:
                print(f"Error adding cookie: {e}")
    except Exception as e:
        print(f"Error loading cookies: {e}")

def login(sb): 
    # load cookies, if they don't work, login
    
    sb.click('a#loginLink')
    sb.type('input#login_user_email', os.getenv('USER'))
    sb.type('input#login_user_password', os.getenv('PASS'))
    sb.click('//*[@id="login_btn_container"]/div/button')
    save_cookies(sb)

def procesar_imagen(path): 

    while True: 
        # get height of image, and adjust for website
        try: 
            with Image.open('imgs/' + path + '.png') as img: 
                width, height = img.size

                new_height = int((290 / width) * height)
                resized_img = img.resize((290, new_height))
                resized_img.save('imgs/' + imagen + "resized.png")

                return new_height
        except Exception as E: 
            print(f'Error al buscar imagen imgs/{path}.png')
            return False

def escoge_color(sb): 

    # click para menú de color
    sb.click('button.color-control-component')
    continuar = True
    
    # loop para continuar en caso de fallar
    while continuar: 
    # escoge color
        print("Escoge los colores (en formato rgb)")
        r = input('r - rojo: ')
        g = input('g - verde: ')
        b = input('b - azul: ')

         # si no es el default (blanco) continuar
        if (r != '255' and g != '255' and b != '255'): 
            try: 
                # loop para buscar el color
                color_selector = f'background-color: rgb({r}, {g}, {b});'
                colors = sb.find_elements('.color-element')
                matches = []
                for color in colors:    
                    if color.get_attribute("style") == color_selector: 
                        matches.append(color)

                for match in matches: 
                    try: 
                        print(match)
                        match.click()
                        break
                    except Exception as e: 
                        print(e)
                
                #print(match)
                #builder.move_by_offset(match['x'], match['y']).click().perform()

                # si funcionó, parar
                continuar = False
            except ElementNotVisibleException as e: 
                print('No se encontró ese color, inténtelo de nuevo')
                print(e)
            except NoSuchElementException as e: 
                print('No se encontró ese color, intentelo de nuevo')
                print(e)


        else: 
            # si es blanco, no se necesita cambiar
            continuar = False


def move_img(sb, by, selector, x_offset, y_offset): 
    # mueve la imágen hacia arriba, para que sea más realista a una camisa de verdad
    img = sb.find_element(selector, by=by)
    action = ActionChains(sb.driver)
    action.click_and_hold(img).move_by_offset(x_offset, y_offset).release().perform()

def guardar_en_archivo(link, archivo): 
    # guarda el link del video en un archivo
    try:
        # Open the file in write mode
        with open(archivo, 'w') as file:
            # Write the text to the file
            file.write(link)
        
    except Exception as e:
        print(f"Un error ocurrió al guardar en el archivo: {e}")
    

# OPCIONES PARA DESCARGAR LOS VIDEOS
# directorio
download_dir = os.path.join(os.getcwd(), "downloads")
if not os.path.exists(download_dir):
    os.makedirs(download_dir)


with SB(uc=True) as sb: # Use Chrome in User-Mode
    sb.open("https://placeit.net/c/mockups/stages/front-and-back-view-bella-canvas-crewneck-tee-video-featuring-a-man-in-a-studio-7515v")

    load_cookies(sb)
    sb.open("https://placeit.net/c/mockups/stages/front-and-back-view-bella-canvas-crewneck-tee-video-featuring-a-man-in-a-studio-7515v")
    # dar al botón de aceptar cookies
    aceptar_cookies(sb)

    # click edit button 
    sb.click("button:contains('Edit')")
    sb.click("div#container aside div:nth-of-type(2) div button div")

    login(sb)

    # esperar después del login
    time.sleep(10)

    
    # loop para conseguir path válido
    while True: 
        # agregar '.png' para imagen original
        # agregar 'resized.png' para imagen modificada
        imagen = input('Nombre del archivo (sin .png): ')
        new_height = procesar_imagen(imagen)

        if new_height != False: 
            break

    offset = 220 - new_height / 2

    # elegir imagen 
    sb.choose_file("input#inputcustomG_0-file-input", 'imgs/' + imagen + "resized.png")
   
    # variable para encontrar imagen
    img = '//*[@id="cropperOverlay"]/div/div/div[2]/div/div[1]/div/img'

    # esperar a que aparezca la imagen
    sb.wait_for_element_visible(img)

    # scroll la imagen 
    move_img(sb, by=By.XPATH, selector=img, x_offset=0, y_offset=-offset)
    
    # crop button
    sb.click("div#cropperOverlay div div:nth-of-type(2) div:nth-of-type(2) div:nth-of-type(4) button")
    # espera a que termine de cargar
    time.sleep(7)

    escoge_color(sb)

    time.sleep(5)
    
    # obtener el link del video
    link = obtener_link(sb)
    guardar_en_archivo(link, 'links.txt')