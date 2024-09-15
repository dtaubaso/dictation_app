import streamlit as st
import edge_tts
import asyncio

# Lista predefinida de palabras
word_list = ["apple", "banana", "orange", "grape", "pineapple"]

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

# Función para generar y reproducir el audio de la palabra
async def generate_audio(word, voice="en-US-AriaNeural"):
    tts = edge_tts.Communicate(word, voice)
    await tts.save("output.mp3")
    st.session_state.audio_played = True  # Marca que el audio se ha generado

def play_audio(file_path):
    with open(file_path, "rb") as audio_file:
        audio_bytes = audio_file.read()
    st.audio(audio_bytes, format="audio/mp3", autoplay=True)

# Lógica principal
def main():
    st.title("Aprender a Escribir en Inglés")

    # Mostrar la palabra actual
    current_word = word_list[st.session_state.current_word]

    # Botón para reproducir la palabra
    if st.button("Reproducir palabra"):
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
            if user_input.lower() == current_word.lower():
                st.success(f"¡Correcto! La palabra es: {current_word}")
                st.session_state.score += 1
            else:
                st.error(f"Incorrecto. La palabra correcta es: {current_word}")

            # Guardar la palabra y si fue correcta o no
            st.session_state.answered_words.append(
                {"word": current_word, "input": user_input, "status": "Correcto" if user_input.lower() == current_word.lower() else "Incorrecto"}
            )

            # Avanzar a la siguiente palabra
            st.session_state.current_word += 1
            st.session_state.audio_played = False  # Reiniciar el estado del audio
            st.session_state.user_input = ""  # Borrar el campo de texto

            # Revisar si hay más palabras
            if st.session_state.current_word >= st.session_state.total:
                st.write(f"Juego terminado. Puntaje: {st.session_state.score}/{st.session_state.total}")
                st.session_state.current_word = 0  # Reiniciar para empezar de nuevo
                st.session_state.score = 0  # Reiniciar puntaje
                st.session_state.answered_words = []  # Reiniciar el historial de palabras
        else:
            st.warning("Por favor, ingresa una palabra.")

    # Mostrar el historial de palabras ya ingresadas
    if st.session_state.answered_words:
        st.subheader("Palabras ya respondidas")
        for entry in st.session_state.answered_words:
            st.write(f"Palabra: {entry['word']} | Tu respuesta: {entry['input']} | Estado: {entry['status']}")

# Ejecutar la app
if __name__ == "__main__":
    main()
