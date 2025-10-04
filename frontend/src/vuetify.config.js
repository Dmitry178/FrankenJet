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

const sky = {
  dark: false,
  colors: {
    primary: '#4A90E2',      // Глубокое небо
    secondary: '#87CEEB',    // Светлое небо
    accent: '#5DADE2',       // Лёгкий акцент
    error: '#C0392B',        // Красный (как на авиационных огнях)
    info: '#3498DB',         // Ясное небо
    success: '#2ECC71',      // Успешный полёт
    warning: '#F39C12',      // Внимание (как огни приземления)
    background: '#E0F6FF',   // Очень светлое небо
    surface: '#FFFFFF',      // Облака
    border: '#AED6F1',       // Лёгкая дымка
  }
}

const skyDark = {
  dark: true,
  colors: {
    primary: '#5DADE2',      // Яркое небо в темноте
    secondary: '#85C1E9',    // Светлое небо при закате
    accent: '#3498DB',       // Акцент как закат
    error: '#E74C3C',        // Авиационная тревога
    info: '#87CEEB',         // Тёмное небо
    success: '#58D68D',      // Успешный полёт
    warning: '#F4D03F',      // Внимание
    background: '#0C2461',   // Глубокое небо (ночь)
    surface: '#1A5276',      // Облака при луне
    border: '#5499C7',       // Лёгкий контур
  }
}

export default {
  theme: {
    defaultTheme: 'light',
    themes: {
      light: light,
      dark: dark,
      sky: sky,
      skyDark: skyDark,
    },
  },
  defaults: {
    VContainer: {
      fluid: true,
      style: 'padding: 10px;',
    },
    VAppBar: {
      elevation: 0,
      flat: true,
      style: 'border-bottom: 1px solid rgb(var(--v-theme-border));',
    },
    VCard: {
      elevation: 0,
      rounded: '2',
      style: 'border: 1px solid rgb(var(--v-theme-border));',
    },
    VTextField: {
      density: 'compact',
      singleLine: true,
      variant: 'outlined',
    },
  },
  icons: {
    defaultSet: 'mdi',
  },
}
