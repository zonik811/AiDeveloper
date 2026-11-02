# Manual Oficial de Estándares de Codificación COBOL y CICS
## Mainsoft Ltda. — Centro de Excelencia (CoE) Mainframe & z/OS
**Versión:** 4.2 | **Clasificación:** Uso Interno | **Fecha de Vigencia:** 2026

---

### 1. Formato de Código Fuente y Estructura de Columnas
En todos los desarrollos sobre entornos IBM Enterprise COBOL para z/OS se debe respetar estrictamente la distribución tradicional de 80 columnas:
- **Columnas 1 a 6 (Número de Secuencia):** Reservadas para numeración de tarjeta o marcas de control histórico.
- **Columna 7 (Indicador):** Reservada para comentarios (`*`), salto de página (`/`) o continuación de líneas no numéricas (`-`).
- **Área A (Columnas 8 a 11):** Reservada exclusivamente para los encabezados de división (`IDENTIFICATION DIVISION`, `ENVIRONMENT DIVISION`, `DATA DIVISION`, `PROCEDURE DIVISION`), nombres de sección, encabezados de párrafos y declaraciones de nivel principal (`01` y `77`).
- **Área B (Columnas 12 a 72):** Reservada para todas las sentencias ejecutables (`MOVE`, `PERFORM`, `IF`, `COMPUTE`), cláusulas de definición de datos subordinados (`02` al `49`, `66`, `88`) y continuación de sentencias.
- **Columnas 73 a 80 (Identificación):** Reservadas para el ID del programa o código de modificación del commit.

---

### 2. Tipos de Datos Numéricos y Reglas para COMP-3 (Packed Decimal)
Para el almacenamiento de montos contables, importes y saldos en aplicaciones bancarias, es obligatorio el uso de formato empaquetado `COMP-3` (Packed Decimal) para optimizar memoria en disco DASD y procesador:
- **Fórmula de almacenamiento en memoria:**
  $$\text{Bytes en disco} = \left\lceil \frac{\text{Número de dígitos} + 1}{2} \right\rceil$$
  Cada byte físico almacena dos dígitos decimales en formato BCD (Binary Coded Decimal), salvo el último medio byte (nibble bajo) que guarda el signo de la variable.
- **Representación del nibble de signo:**
  - `C` (hexadecimal): Número positivo con signo (`+`).
  - `D` (hexadecimal): Número negativo con signo (`-`).
  - `F` (hexadecimal): Número sin signo o positivo por omisión.
- **Prevención de ABEND S0C7:** Toda variable `COMP-3` debe ser inicializada explícitamente (`INITIALIZE` o `VALUE ZEROES`) antes de cualquier cálculo aritmético. Operar sobre campos sin inicializar provocará un ABEND de excepción de datos (S0C7).

---

### 3. Estándares Transaccionales CICS y Finalización de Programas
Los programas que operan bajo el monitor transaccional IBM CICS Transaction Server deben cumplir con las reglas de concurrencia y gestión de recursos:
- **Prohibición de STOP RUN y GOBACK sin control:** Está terminantemente prohibido utilizar la instrucción `STOP RUN` o `GOBACK` fuera del control de CICS, ya que esto finaliza el hilo del Address Space del sistema y puede desestabilizar la región CICS completa afectando a miles de usuarios.
- **Finalización Correcta:** Toda transacción debe concluir ordenadamente mediante el comando:
  `EXEC CICS RETURN [TRANSID(...)] [COMMAREA(...)] END-EXEC.`
- **Abortos y Rollbacks Programados:** Cuando ocurra una condición de error de negocio irrecuperable, se debe forzar un rollback sincrónico de las unidades de trabajo lógicas (LUW) usando:
  `EXEC CICS ABEND ABCODE('xxxx') END-EXEC.`
- **Transferencia de Datos:** El intercambio de memoria entre programas debe realizarse a través de la `DFHCOMMAREA` validando siempre su longitud contra `EIBCALEN`.

---

### 4. Acceso a Bases de Datos Relacionales DB2 y Bloque DFHEIBLK
En programas que combinen CICS y DB2:
- **Evaluación de SQLCODE:** Inmediatamente después de cada comando `EXEC SQL`, es mandatorio evaluar la variable `SQLCODE` en la `SQLCA`.
  - `0`: Ejecución exitosa.
  - `+100`: Registro no encontrado (`NOT FOUND`).
  - `< 0`: Error crítico (rollback requerido).
- **Evaluación de Comandos CICS:** En cada comando CICS ejecutado, se debe verificar el campo `EIBRESP` del bloque de interfaz de ejecución `DFHEIBLK` comparándolo contra la función integrada `DFHRESP(NORMAL)`. Se prohíbe evaluar códigos numéricos duros sin la función `DFHRESP`.

---

### 5. Convenciones de Nomenclatura en la WORKING-STORAGE SECTION
Para mantener la legibilidad y facilitar el mantenimiento de sistemas legacy:
- **`WS-`**: Prefijo mandatorio para variables de trabajo internas de proceso (ej. `WS-MONTO-TOTAL`, `WS-FECHA-PROCESO`).
- **`SW-`**: Prefijo mandatorio para variables de control lógico y banderas tipo booleano con cláusula nivel `88` (ej. `SW-FIN-ARCHIVO`).
- **`TAB-`**: Prefijo obligatorio para arrays y tablas internas cargadas en memoria (ej. `TAB-CODIGOS-BANCO`).
- **`CTR-`**: Prefijo reservado para variables de contadores acumulativos en bucles de lectura batch.
- Queda prohibido el uso de nombres genéricos como `AUX`, `VAR1`, `TEMP` o variables de una sola letra.
