document.addEventListener('DOMContentLoaded', () => {
    const registerButton = document.getElementById('register-button');
    const loginButtonInRegister = document.getElementById('login-button');
    const loginForm = document.getElementById('login-form');
    const registerForm = document.getElementById('register-form');
    const registroMensaje = document.getElementById('registro-mensaje');
    const loginSubmitButton = document.getElementById('login-submit');
    const loginMensaje = document.getElementById('login-mensaje');
    const registerSubmitButton = document.getElementById('register-submit');

    if (registerButton && loginButtonInRegister && loginForm && registerForm) {
        registerButton.addEventListener('click', () => {
            loginForm.classList.add('hidden');
            registerForm.classList.remove('hidden');
        });

        loginButtonInRegister.addEventListener('click', () => {
            registerForm.classList.add('hidden');
            loginForm.classList.remove('hidden');
        });
    } else {
        console.error('Elementos de cambio de formulario no encontrados en el DOM.');
    }

    if (registerSubmitButton && registerForm && registroMensaje) {
        registerForm.addEventListener('submit', async (event) => {
            event.preventDefault();

            const email = document.getElementById('register-email').value;
            const password = document.getElementById('register-password').value;
            const dni = document.getElementById('register-dni').value;

            const userData = {
                email: email,
                contrasena: password,
                dni: dni
            };

            try {
                const response = await fetch('/registro', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(userData)
                });

                const data = await response.json();

                if (response.ok) {
                    registroMensaje.textContent = 'Registro exitoso!';
                    registroMensaje.className = 'mt-4 text-sm text-green-500';
                    // Aquí podrías redirigir al usuario o hacer otras acciones
                } else {
                    registroMensaje.textContent = `Error en el registro: ${data.message || 'Algo salió mal'}`;
                    registroMensaje.className = 'mt-4 text-sm text-red-500';
                }

            } catch (error) {
                console.error('Error al enviar la petición de registro:', error);
                registroMensaje.textContent = 'Error de conexión con el servidor.';
                registroMensaje.className = 'mt-4 text-sm text-red-500';
            }
        });
    } else {
        console.error('Elementos del formulario de registro no encontrados en el DOM.');
    }

    if (loginSubmitButton && loginForm && loginMensaje) {
        loginForm.addEventListener('submit', async (event) => {
            event.preventDefault();

            const email = document.getElementById('login-email').value;
            const password = document.getElementById('login-password').value;

            const userData = {
                email: email,
                password: password
            };

            try {
                const response = await fetch('/login', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(userData)
                });

                const data = await response.json();

                if (response.ok) {
                    loginMensaje.textContent = 'Login exitoso!';
                    loginMensaje.className = 'mt-4 text-sm text-green-500';
                    // Aquí podrías redirigir al usuario o hacer otras acciones,
                    // como guardar la información de la sesión.
                    console.log('Login exitoso:', data);
                } else if (response.status === 401) {
                    loginMensaje.textContent = 'Credenciales incorrectas.';
                    loginMensaje.className = 'mt-4 text-sm text-red-500';
                } else if (response.status === 404) {
                    loginMensaje.textContent = 'Usuario no encontrado.';
                    loginMensaje.className = 'mt-4 text-sm text-red-500';
                } else {
                    loginMensaje.textContent = `Error en el login: ${data.message || 'Algo salió mal'}`;
                    loginMensaje.className = 'mt-4 text-sm text-red-500';
                }

            } catch (error) {
                console.error('Error al enviar la petición de login:', error);
                loginMensaje.textContent = 'Error de conexión con el servidor.';
                loginMensaje.className = 'mt-4 text-sm text-red-500';
            }
        });
    } else {
        console.error('Elementos del formulario de login no encontrados en el DOM.');
    }
});

const tableReservationForm = document.getElementById('table-reservation-form');
    const reservationMessage = document.getElementById('reservation-message'); // Vamos a añadir este elemento al HTML

    if (tableReservationForm) {
        tableReservationForm.addEventListener('submit', async (event) => {
            event.preventDefault();

            const fecha = document.getElementById('reservation-date').value;
            const hora = document.getElementById('reservation-time').value;
            const numeroPersonas = document.getElementById('reservation-guests').value;

            const reservationData = {
                fecha: fecha,
                hora: hora,
                numero_personas: numeroPersonas
            };

            try {
                const response = await fetch('/reservar_mesa', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(reservationData)
                });

                const data = await response.json();

                if (response.ok) {
                    reservationMessage.textContent = 'Reserva realizada con éxito!';
                    reservationMessage.className = 'mt-4 text-sm text-green-500';
                    tableReservationForm.reset(); // Limpiar el formulario
                } else {
                    reservationMessage.textContent = `Error al reservar: ${data.message || 'Algo salió mal'}`;
                    reservationMessage.className = 'mt-4 text-sm text-red-500';
                }

            } catch (error) {
                console.error('Error al enviar la petición de reserva:', error);
                reservationMessage.textContent = 'Error de conexión con el servidor.';
                reservationMessage.className = 'mt-4 text-sm text-red-500';
            }
        });
    } else {
        console.error('El formulario de reserva de mesa no fue encontrado en el DOM.');
    }