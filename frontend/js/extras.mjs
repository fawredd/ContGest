const extras = {
    sanitizeFilename: function (filename) {
        if(0){
        // Eliminar acentos
        filename = filename.normalize('NFD').replace(/[\u0300-\u036f]/g, '');
      
        // Reemplazar espacios por guiones bajos
        filename = filename.replace(/ /g, '_');
      
        // Eliminar caracteres no válidos
        filename = filename.replace(/[^\w\d_\-.]/g, '');
        }
        return filename;
      },
      esArchivoPermitido: function(file) {
        const extensionesPermitidas = ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.jpg', '.jpeg', '.png', '.gif', '.tif'];
        const nombreArchivo = file.name;
        const extension = nombreArchivo.substring(nombreArchivo.lastIndexOf('.')).toLowerCase();
        return extensionesPermitidas.includes(extension);
      }
};

export default extras;