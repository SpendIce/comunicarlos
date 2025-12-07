// Script de inicialización de MongoDB
// Se ejecuta automáticamente cuando se crea el contenedor por primera vez

db = db.getSiblingDB('mesa_ayuda_db');

// Crear colecciones
db.createCollection('usuarios');
db.createCollection('requerimientos');
db.createCollection('servicios');
db.createCollection('notificaciones');
db.createCollection('counters');

// Inicializar contadores de secuencias
db.counters.insertMany([
    { _id: 'usuario_id', sequence_value: 0 },
    { _id: 'requerimiento_id', sequence_value: 0 },
    { _id: 'servicio_id', sequence_value: 0 },
    { _id: 'notificacion_id', sequence_value: 0 }
]);

// Crear índices
db.usuarios.createIndex({ "email": 1 }, { unique: true });
db.usuarios.createIndex({ "tipo_usuario": 1 });

db.requerimientos.createIndex({ "solicitante_id": 1 });
db.requerimientos.createIndex({ "tecnico_asignado_id": 1 });
db.requerimientos.createIndex({ "estado": 1 });
db.requerimientos.createIndex({ "tipo": 1 });
db.requerimientos.createIndex({ "fecha_creacion": -1 });
db.requerimientos.createIndex({ "estado": 1, "fecha_creacion": -1 });

db.servicios.createIndex({ "solicitante_id": 1 });
db.servicios.createIndex({ "activo": 1 });

db.notificaciones.createIndex({ "supervisor_id": 1 });
db.notificaciones.createIndex({ "leida": 1 });
db.notificaciones.createIndex({ "supervisor_id": 1, "leida": 1 });

print('✅ Base de datos inicializada correctamente');

