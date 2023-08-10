import extras from './extras.mjs';

const { createApp } = Vue;

const app = Vue.createApp({
  data() {
    return {
    asiento: {
      id: 0,
      operacion: '',
      fechaRegistro: new Date().toISOString().slice(0, 10),
      fechaMovimiento: new Date().toISOString().slice(0, 10),
      detalle: '',
      estado: 0,
      adjuntosAsientos: [], /* TENGO QUE CORREGIR ESTA VARIABLE YA QUE EN BACKEND ES # ADJUNTOS # */
      transacciones: [
        {
          movimiento: 0,
          tc: 1.0,
          cuenta: 0,
          detalle: '',
          estado: 0
        },
        {
          movimiento: 0,
          tc: 1.0,
          cuenta: 0,
          detalle: '',
          estado: 0
        }
      ]
    },
    cuentas: [],
    operaciones: [],
    colDerecha:{
      cargando: true
    },
    colIzquierda:{
      cargando: true
    },
    transacciones: [
      {
        id:0,
        cuenta:0,
        detalleAsiento:'',
        detalleTransaccion: '',
        fechaRegistro:'',
        fechaMovimiento:'',
        id:0,
        movimiento: 0,
        operacion:0,
        asiento:0
      }
    ]
  }
  },
  methods: {
    addTransaccion() {
      this.asiento.transacciones.push({
        movimiento: 0,
        tc: 1.0,
        cuenta: 0,
        detalle: '',
        estado: 0
      });
    },
    deleteTransaccion(index) {
      this.asiento.transacciones.splice(index, 1);
    },
    createAsiento() {
      this.colIzquierda.cargando = true;
      var chequeo = 1;
      // Convertir el valor del campo 'movimiento' a número
      this.asiento.transacciones.forEach(transaccion => {
        transaccion.movimiento = Number(transaccion.movimiento);
        if(transaccion.movimiento == 0){
          alert("Los movimientos no pueden ser cero.\n Quedan marcados con borde rojo.");
          chequeo = 0;
        }
      });
      
      if (chequeo == 1){
        const formData = new FormData();
        const inputElement = this.$refs.losAdjuntos;
        const fileList = inputElement.files;
        
        for (var i = 0; i < fileList.length; i++ ){
          let file = fileList[i];
          if (extras.esArchivoPermitido(file)){
            const fileEnServer = extras.sanitizeFilename(file.name);
            formData.append(file.name, file);
            this.asiento.adjuntosAsientos.push(
              { 
                adjunto: `${fileEnServer}` ,
                detalle: `Nombre del archivo agregado ${fileEnServer}`,
                estado:0
               }
               );
          } else {
            console.log("Se descarto el archivo " + file.name)
          }
        }
        formData.append('asiento', JSON.stringify(this.asiento));
        axios.post('https://fawredd.pythonanywhere.com/asientos', formData,{
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        })
          .then(response => {
            alert('Asiento creado exitosamente');
            this.asiento = {
              operacion: '',
              fechaRegistro: new Date().toISOString().slice(0, 10),
              fechaMovimiento: new Date().toISOString().slice(0, 10),
              detalle: '',
              aduntosAsientos: [
                {
                  adjunto:'',
                  detalle:'',
                  estado:0
                }
              ],
              transacciones: [
                {
                  movimiento: 0,
                  tc: 1.0,
                  cuenta: 0,
                  detalle: '',
                  estado: 0
                }
              ]
            };
          })
          .catch(error => {
            console.log(error);
            alert('Ha ocurrido un error al crear el asiento');
          });
      }
      this.colIzquierda.cargando = true;
    },
    get_cuentas(){
        /* Cargo todas las cuentas del plan de cuentas */
      axios.get('https://fawredd.pythonanywhere.com/cuentas')
      .then(response => {
        this.cuentas = response.data;
      })
      .catch(error => {
        console.log(error);
        alert('Ha ocurrido un error al cargar las cuentas');
      });
    },
    get_operaciones(){
      console.log("getOperaciones");
      /* Cargo todas las operaciones */  
      axios.get('https://fawredd.pythonanywhere.com/operaciones')
      .then(response => {
        this.operaciones = response.data;
      })
      .catch(error => {
        console.log(error);
        alert('Ha ocurrido un error al cargar las operaciones');
      });  
    },
    eliminarAdjunto(index) { //Elimina un adjunto de la lista de adjuntos
      console.log("eliminoAdjunto");
      this.asiento.adjuntosAsientos.splice(index, 1);
    },
    agregoAdjuntos(){
      console.log("agregoAdjunto");
      this.asiento.adjuntosAsientos = [];
      for (var i = 0; i < this.$refs.losAdjuntos.files.length; i++ ){
        let file = this.$refs.losAdjuntos.files[i];
        // Verifico si el nombre del archivo ya existe en el arreglo
        let existeArchivo = this.asiento.adjuntosAsientos.some(adjunto => adjunto.adjunto === file.name);
        if (extras.esArchivoPermitido(file) && !existeArchivo){
          console.log(`Se cargo el archivo ${file.name}`);
          this.asiento.adjuntosAsientos.push(
            { 
              adjunto: `${file.name}` ,
              detalle: `Nombre del archivo agregado ${file.name}`,
              estado:0
             }
             );
        } else {
          console.log("Se descarto el archivo " + file.name)
        }  
      }
    },
    get_transacciones(cuenta){
      this.colDerecha.cargando = true;
      /* Cargo las transacciones asociadas a una cuenta */  
      axios.get(`https://fawredd.pythonanywhere.com/cuentas/${cuenta}`)
      .then(response => {
        this.transacciones = response.data;
        this.colDerecha.cargando = false;
      })
      .catch(error => {
        console.log(error);
        alert('Ha ocurrido un error al cargar las transacciones');
      });  
    },
    muestraDetalle(transaccion){
      return (transaccion.detalleAsiento + ((transaccion.detalleTransaccion==null)?'':(" / " + transaccion.detalleTransaccion)));
    },
    formatoFecha(fecha) {
      const opciones = { day: '2-digit', month: '2-digit', year: 'numeric' };
      return new Date(fecha).toLocaleDateString('es-AR', opciones); // Cambiar a tu formato deseado
    },
    formatoNumero(valor) {
      return valor.toLocaleString(undefined, {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2,
        useGrouping: true
      }).replace(/,/g, "."); // le doy formato a los numeros con el tipo #0.00
    },
    cargaAsiento(id){
      this.colIzquierda.cargando = true;
      /* Cargo las transacciones asociadas a una cuenta */  
      axios.get(`https://fawredd.pythonanywhere.com/asientos/${id}`)
      .then(response => {
        this.asiento = response.data;
      })
      .catch(error => {
        console.log(error);
        alert('Ha ocurrido un error al cargar las transacciones');
      });  
      this.colIzquierda.cargando = false;
    }
  },
  mounted(){
    Promise.all([this.get_cuentas(), this.get_operaciones()])
    .then(() => {
      // Código adicional que se ejecutará después de que ambas promesas hayan concluido
      this.colIzquierda.cargando = false;
      console.log(`Instancia Vue montada.`);
    })
    .catch(error => {
      // Manejo de errores
      console.error(error);
    });
    this.get_transacciones(5);
  },
  computed: {
    totalTransacciones: function() {
      var elTotal = 0;
      this.asiento.transacciones.forEach(transaccion => {
        elTotal += Number(transaccion.movimiento);
      });
      return Number(elTotal).toFixed(2);
    },
    saldos() {
      let saldo = 0;
      return this.transacciones.map((t) => {
        saldo += Number(t.movimiento);
        return saldo;
      });
    }
  },
  watch:{
    asiento: {
      handler(nuevoValor, viejoValor) {
        console.log(JSON.stringify(nuevoValor));
      },
      deep: true // observar cambios en propiedades anidadas del objeto asiento
    }
  }
});

/* Registro VueSelect */
app.component('v-select', VueSelect.VueSelect);
// Only works if using in-browser compilation.
// If using build tools, see config examples below.
//app.config.compilerOptions.isCustomElement = (tag) => tag.includes('v-select');
app.mount('#app'); /* Mount vue app */
