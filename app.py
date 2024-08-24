from flask import Flask, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import WebDriverException
import seaborn as sns
import matplotlib
matplotlib.use('Agg')  # Usar el backend 'Agg' para evitar problemas de GUI
import matplotlib.pyplot as plt
import pandas as pd

app = Flask(__name__)

def scrape_data():
    driver = webdriver.Chrome()
    
    try:
        url = 'https://books.toscrape.com/'
        driver.get(url)
        driver.implicitly_wait(10)
        
        elementos = driver.find_elements(By.CSS_SELECTOR, 'ol.row > li')
        datos = []

        for elemento in elementos:
            titulo = elemento.find_element(By.CSS_SELECTOR, 'h3 > a').get_attribute('title')
            precio = elemento.find_element(By.CSS_SELECTOR, '.price_color').text
            datos.append({'Título': titulo, 'Precio': float(precio[1:])})  # Convertimos el precio a float

        return datos

    except WebDriverException as e:
        print(f"WebDriver error: {e}")
        return []

    finally:
        driver.quit()

@app.route('/api/scrape_books', methods=['GET'])
def scrape_books():
    data = scrape_data()
    
    # Crear DataFrame
    df = pd.DataFrame(data)
    
    # Crear gráficos con Seaborn
    sns.set(style="whitegrid")
    
    # Gráfico categórico
    plt.figure(figsize=(10, 6))
    sns.countplot(y='Título', data=df)
    plt.title('Cantidad de libros por Título')
    plt.savefig('grafico_categorico.png')
    plt.close()
    
    # Gráfico relacional
    plt.figure(figsize=(10, 6))
    sns.scatterplot(x='Título', y='Precio', data=df)
    plt.title('Relación entre Título y Precio')
    plt.savefig('grafico_relacional.png')
    plt.close()
    
    # Gráfico de distribución
    plt.figure(figsize=(10, 6))
    sns.histplot(df['Precio'], kde=True)
    plt.title('Distribución de Precios')
    plt.savefig('grafico_distribucion.png')
    plt.close()
    
    # Crear el documento Quarto
    with open('analisis_libros.qmd', 'w') as file:
        file.write("""
        ---
        title: "Análisis de libros"
        format: html
        ---
        
        ```{r}
        library(ggplot2)
        library(gridExtra)
        ``` 
        
        ## Gráfico Categórico
        
        ![Gráfico Categórico](grafico_categorico.png)
        
        ## Gráfico Relacional
        
        ![Gráfico Relacional](grafico_relacional.png)
        
        ## Gráfico de Distribución
        
        ![Gráfico de Distribución](grafico_distribucion.png)
        """)
    
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)
