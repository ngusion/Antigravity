/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            colors: {
                jarvis: {
                    bg: '#0f172a',
                    accent: '#0ea5e9',
                    text: '#e2e8f0'
                }
            }
        },
    },
    plugins: [],
}
