const light = {
  dark: false,
  colors: {
    primary: '#CDAB8F',
    secondary: '#E8D5C4',
    accent: '#A1887F',
    error: '#B00020',
    info: '#2196F3',
    success: '#4CAF50',
    warning: '#F0F000',
    background: '#f5f5f0',
    surface: '#FFFDF5',
    border: '#DBC0AA',
  }
}

const dark = {
  dark: true,
  colors: {
    primary: '#9E9E9E',
    secondary: '#757575',
    accent: '#BDBDBD',
    error: '#FFBABA',
    info: '#89CFF0',
    success: '#90EE90',
    warning: '#C0C000',
    background: '#333333',
    surface: '#555555',
    border: '#777777',
  }
}

const skyDeep = {
  dark: true,
  colors: {
    primary: '#1177FF',
    secondary: '#5C9BFF',
    accent: '#8BB8FF',
    error: '#FF6B6B',
    info: '#1177FF',
    success: '#51CF66',
    warning: '#B0B000',
    background: '#0D0F15',
    surface: '#1A1D26',
    border: '#2D323E',
  }
}

const sky = {
  dark: false,
  colors: {
    primary: '#4A90E2',
    secondary: '#87CEEB',
    accent: '#5DADE2',
    error: '#C0392B',
    info: '#3498DB',
    success: '#2ECC71',
    warning: '#F39C12',
    background: '#E0F6FF',
    surface: '#FFFFFF',
    border: '#AED6F1',
  }
}

const skyDark = {
  dark: true,
  colors: {
    primary: '#5DADE2',
    secondary: '#85C1E9',
    accent: '#3498DB',
    error: '#E74C3C',
    info: '#87CEEB',
    success: '#58D68D',
    warning: '#F4D03F',
    background: '#0C2461',
    surface: '#1A5276',
    border: '#5499C7',
  }
}

export default {
  theme: {
    defaultTheme: 'light',
    themes: {
      light: light,
      dark: dark,
      skyDeep: skyDeep,
      // sky: sky,
      // skyDark: skyDark,
    },
  },
  defaults: {
    VContainer: {
      fluid: true,
      class: 'py-2 pt-sm-4 pb-sm-0',
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
      class: 'mb-2 mb-sm-4',
    },
    VCardTitle: {
      class: 'ma-0 pa-0 px-sm-4 py-sm-3 mx-sm-3',
    },
    VCardText: {
      class: 'ma-0 pa-0 px-sm-4 pb-sm-4 mx-sm-3',
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
