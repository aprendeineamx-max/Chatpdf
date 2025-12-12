/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            colors: {
                'cortex-bg': '#0f172a',
                'cortex-panel': '#1e293b',
                'cortex-accent': '#3b82f6',
                'cortex-text': '#f8fafc',
            },
        },
    },
    plugins: [
        require('@tailwindcss/typography'),
    ],
}
