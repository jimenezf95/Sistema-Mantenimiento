# config.py

# Configuración de checklists para cada tipo de máquina
checklists_por_tipo = {

    "Compactadora": [
        "Unidad Hidráulica",
        "Cilindro Hidráulico",
        "Conexiones Eléctricas",
        "Activador de Placa Compactadora",
        "Tablero de Control",
        "Sistema de Cierre",
        "Mecanismo de Expulsión",
        "Puerta de Extracción"
    ],

    "Briqueteadora": {
        "Dispositivos eléctricos y mecánicos": [
            "Estado de cables y conexiones",
            "Estado de caja eléctrica",
            "Interfáz de Control (Pulsadores)",
            "Motor Eléctrico en BRIQUETEADORA",
            "Motor Eléctrico en COMPRESOR",
            "Conexión de sensores de posición"
        ],
        "Dispositivos de seguridad": [
            "Pulsador de Parada de Emergencia",
            "Guarda de seguridad en la transmisión",
            "Guarda de seguridad en compuerta de expulsión Briqueta"
        ],
        "Sistema neumático": [
            "Estado Bomba Hidráulica (Revisar Fugas)",
            "Estado Mangueras del Compresor",
            "Sin Fugas en la Unidad Hidráulica",
            "Estado tuberías y acoples",
            "Estado de Manómetros"
        ],
        "Factor humano y operación": [
            "Puesto de trabajo ordenado y sin sustancias deslizantes",
            "Cabina de compactación libre de materiales diferentes al POTE",
            "Elementos de Protección Personal completos (Casco, Guantes, Botas, Tapaoidos, Gafas y Mascarilla)"
        ]
    },

    "Montacargas": {
        "Fluidos / Motor": [
            "Aceite Motor",
            "Líquido hidráulico",
            "Refrigerante",
            "Electrolito Batería",
            "Sistema Eléctrico",
            "Mangueras/Correas",
            "Filtro de Aire",
            "Filtro Gasolina/ACPM",
            "Correa",
            "Líquido de Frenos"
        ],
        "Sistema de elevación": [
            "Horquillas o Trinches",
            "Torre o Mástil",
            "Mangueras Hidráulicas",
            "Cadenas",
            "Rodamientos",
            "Cilindros",
            "Fugas de hidráulico",
            "Sustentación de Carga",
            "Palancas"
        ],
        "Estado general del equipo": [
            "Apariencia del Equipo",
            "Equipo Limpio y Aseado",
            "Luces de Estacionamiento",
            "Freno de Estacionamiento",
            "Estructura Antivuelco (ROPS)",
            "Pito Delantero",
            "Pito de Retroceso",
            "Baliza",
            "Pedales en buen Estado",
            "Llantas en buen Estado",
            "Pernos completos"
        ],
        "Cabina": [
            "Cinturón de Seguridad",
            "Silla en buen Estado",
            "Luces de Servicio",
            "Direccionales",
            "Luces de Freno",
            "Luces de Reversas",
            "Indicadores de Tablero",
            "Espejos Laterales",
            "Horómetro",
            "Indicador Aceite y Refrigerante"
        ]
    },

    "Cizalladora": {
        "Dispositivos eléctricos": [
            "Estado de cables y conexiones",
            "Interfáz de Control en buen estado (Pulsadores)"
        ],
        "Seguridad": [
            "Guarda de protección de corte",
            "Verificación paro de emergencia"
        ],
        "Sistema de lubricación": [
            "Sin fugas en unidad hidráulica",
            "Mangueras y cilindro hidráulico en buen estado"
        ],
        "Sistema de corte y accionamiento": [
            "Estado de cuchillas y posición de corte",
            "Estado Funcionamiento del Motor",
            "Funcionamiento del pedal (si aplica)",
            "Palanca de accionamiento (si aplica)"
        ],
        "Factor humano": [
            "Uso de Elementos de Protección Personal COMPLETOS"
        ]
    },

    "Herramienta Manual y Potencia": [
        "Llenar",
        "Llenar"
    ],

    "Equipo Oxicorte": {
        "Estructura general": [
            "Carro general",
            "Sistema de ruedas",
            "Sistema de sujeción de cilindros",
            "Protector de discos"
        ],
        "Cilindros y conexiones": [
            "Llave de paso de acetileno",
            "Llave de paso de oxígeno",
            "Estado visual/Mangueras en buen estado"   
        ],
        "Conjunto de manómetros": [
            "Cubierta de manómetro",
            "Fuga de conexión",
            "Apriete de abrazaderas",
            "Estado y funcionamiento de regulador",
            "Válvula contra llamas"
        ],
        "Otros": [
            "Instrucciones de operación",
            "Avisos de prohibido fumar",
            "Cortador",
            "Boquillas",
            "Gafas para Oxicorte",
            " Peto de Carnaza para operario",
            "Guantes de Carnaza largos",
            "Encendedor de chispa"
        ]
    },
    
    "General": [        
        "Nivel de aceite",
        "Fugas hidráulicas",
        "Estado de orugas",
        "Revisión cucharón",
        "Luces y señales",
        "Limpieza general"
    ]
}