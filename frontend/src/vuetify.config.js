const light = {
  dark: false,
  colors: {
    primary: '#CDAB8F',
    secondary: '#E8D5C4',
    accent: '#A1887F',
    error: '#B00020',
    info: '#2196F3',
    success: '#4CAF50',
    warning: '#FB8C00',
    background: '#F8F5F0',
    surface: '#FFFDF5',
    border: '#DBC0AA',
  }
}

const dark = {
  dark: true,
  colors: {
    primary: '#A1887F',
    secondary: '#CDAB8F',
    accent: '#E8D5C4',
    error: '#FFBABA',
    info: '#89CFF0',
    success: '#90EE90',
    warning: '#FFD700',
    background: '#333333',
    surface: '#555555',
    border: '#777777',
  }
}

export default {
  theme: {
    defaultTheme: 'light',
    themes: {
      light: light,
      dark: dark,
    },
  },
  defaults: {
    VCard: {
      elevation: 0,
      rounded: 'none',
      style: 'border: 1px solid rgb(var(--v-theme-border));',
    },
    VAppBar: {
      elevation: 0,
      flat: true,
      style: 'border-bottom: 1px solid rgb(var(--v-theme-border));',
    },
    VContainer: {
      style: 'padding: 10px;',
    },
  },
}
