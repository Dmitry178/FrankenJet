const logo = `
 _____               _                ___      _   
|  ___|             | |              |_  |    | |  
| |_ _ __ __ _ _ __ | | _____ _ __     | | ___| |_ 
|  _| '__/ _\` | '_ \\| |/ / _ \\ '_ \\    | |/ _ \\ __|
| | | | | (_| | | | |   <  __/ | | /\\__/ /  __/ |_ 
|_| |_|  \\__,_|_| |_|_|\\_\\___|_| |_\\____/ \\___|\\__|
`;

const tagline = `
FrankenJet, энциклопедия истории авиации.
Дмитрий Одегов, https://odegov.pro  
`;

export const displayAsciiArt = () => {
  console.log('%c' + logo, 'font-family: monospace; font-weight: bold;');
  console.log('%c' + tagline, 'font-family: monospace; font-weight: normal;');
};
