import streamlit as st
import edge_tts, random
import asyncio, gspread, json, base64

st.set_page_config(page_title="Dictation App", page_icon=":uk:")

credentials = credentials = base64.b64decode(st.secrets['CREDENTIALS'])

def load_wordlist():
    gc = gspread.service_account_from_dict(json.loads(credentials))
    sheet_id = "1hXHDMMAFB0zosJ_6Aqbp9UIaCU_U9KY3bwac9iQxiWo"
    word_list = gc.open_by_key(sheet_id).get_worksheet(0).col_values(1)
    return word_list

if 'word_list' not in st.session_state:
    st.session_state.word_list = load_wordlist()
word_list = st.session_state.word_list  # Usamos la lista de palabras descargada una vez

# Estado inicial para seguir la palabra actual
if 'current_word' not in st.session_state:
    st.session_state.current_word = 0
if 'score' not in st.session_state:
    st.session_state.score = 0
if 'total' not in st.session_state:
    st.session_state.total = len(word_list)
if 'answered_words' not in st.session_state:
    st.session_state.answered_words = []
if 'audio_played' not in st.session_state:
    st.session_state.audio_played = False
if 'user_input' not in st.session_state:
    st.session_state.user_input = ""  # Estado para el campo de texto
if 'game_over' not in st.session_state:
    st.session_state.game_over = False  # Estado para indicar si el juego ha terminado

# Función para generar y reproducir el audio de la palabra
async def generate_audio(word, voice="en-US-AriaNeural"):
    tts = edge_tts.Communicate(word, voice)
    await tts.save("output.mp3")
    st.session_state.audio_played = True  # Marca que el audio se ha generado

def play_audio(file_path):
    with open(file_path, "rb") as audio_file:
        audio_bytes = audio_file.read()
    st.audio(audio_bytes, format="audio/mp3", autoplay=True)

# Función para reiniciar el juego
def reset_game():
    st.session_state.current_word = 0
    st.session_state.score = 0
    st.session_state.answered_words = []
    st.session_state.audio_played = False
    st.session_state.user_input = ""
    st.session_state.game_over = False

# Lógica principal
def main():

    # Agregar una imagen antes del título
    st.image('https://i.imgur.com/ALJYlX1.png')
    st.title("Dictation App")

    if not st.session_state.game_over:  # Mostrar solo si el juego no ha terminado
        if st.session_state.current_word < len(word_list):
            current_word = word_list[st.session_state.current_word]

    # Mostrar la palabra actual
    # current_word = word_list[st.session_state.current_word]

            # Botón para reproducir la palabra
            if st.button("Escuchar palabra"):
                asyncio.run(generate_audio(current_word))  # Genera el audio

            # Solo reproducir el audio si se ha generado
            if st.session_state.audio_played:
                play_audio("output.mp3")

            # Campo de texto para que el usuario ingrese la palabra, con valor almacenado en session_state
            user_input = st.text_input("Escribe la palabra que escuchaste:", 
                                    value=st.session_state.user_input, 
                                    key="input_text",
                                    on_change=lambda: st.session_state.update({"user_input": st.session_state.input_text}))
            # Botón de envío para validar la palabra ingresada
            if st.button("Enviar"):
                if user_input:
                    # Verificar si es correcto
                    if user_input.lower().strip() == current_word.lower():
                        st.success(f"¡Correcto! La palabra es: {current_word}")
                        st.session_state.score += 1
                    else:
                        st.error(f"Incorrecto. La palabra correcta es: {current_word}")

                    # Guardar la palabra y si fue correcta o no
                    st.session_state.answered_words.append(
                        {"word": current_word, "input": user_input, "status": "correcta" 
                         if user_input.lower() == current_word.lower() else "incorrecta"}
                    )

                    # Avanzar a la siguiente palabra
                    st.session_state.current_word += 1
                    st.session_state.audio_played = False  # Reiniciar el estado del audio
                    st.session_state.user_input = ""  # Borrar el campo de texto

                else:
                    st.warning("Por favor, ingresa una palabra.")

        # Mostrar el resultado del juego si terminó
    if st.session_state.current_word >= len(word_list) or st.session_state.game_over:
        st.session_state.game_over = True
        st.subheader(f":red[Juego terminado. Puntaje: {st.session_state.score}/{len(word_list)}]")
        
        # Botón para reiniciar el juego
        if st.button("Reiniciar"):
            reset_game()
            st.rerun()

    # Mostrar el historial de palabras ya ingresadas
    if st.session_state.answered_words:
        st.write(":blue[**Palabras ya respondidas**]")
        for entry in st.session_state.answered_words:
            st.write(f"""Palabra: **{entry['word']}** | Tu respuesta "{entry['input']}" es {entry['status']}""")

# Ejecutar la app
if __name__ == "__main__":
    main()
