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

# Función para generar el audio de la palabra
async def generate_audio(word, voice="en-US-AvaNeural"):
    tts = edge_tts.Communicate(word, voice)
    await tts.save("output.mp3")

def play_audio(file_path):
    with open(file_path, "rb") as audio_file:
        audio_bytes = audio_file.read()
    st.audio(audio_bytes, format="audio/mp3")

# Lógica principal
def main():
    st.title("Aprender a Escribir en Inglés")

    # Mostrar la palabra actual
    current_word = word_list[st.session_state.current_word]

    # Reproducir el audio de la palabra actual
    if st.button("Reproducir palabra"):
        asyncio.run(generate_audio(current_word))
        play_audio("output.mp3")
    
    # Campo de texto para que el usuario ingrese la palabra
    user_input = st.text_input("Escribe la palabra que escuchaste:")

    if st.button("Enviar") or st.session_state.get("enter_pressed"):
        if user_input:
            # Verificar si es correcto
            if user_input.lower() == current_word.lower():
                st.success(f"¡Correcto! La palabra es: {current_word}")
                st.session_state.score += 1
            else:
                st.error(f"Incorrecto. La palabra correcta es: {current_word}")
            
            # Avanzar a la siguiente palabra
            st.session_state.current_word += 1
            
            # Revisar si hay más palabras
            if st.session_state.current_word >= st.session_state.total:
                st.write(f"Juego terminado. Puntaje: {st.session_state.score}/{st.session_state.total}")
                st.session_state.current_word = 0  # Reiniciar para empezar de nuevo
                st.session_state.score = 0  # Reiniciar puntaje
        else:
            st.warning("Por favor, ingresa una palabra.")

# Ejecutar la app
if __name__ == "__main__":
    main()