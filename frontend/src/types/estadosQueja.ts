
export type EstadoQuejaCode = "PEN" | "ENP" | "RES" | "REC";

export const ESTADO_LABEL: Record<EstadoQuejaCode, string> = {
  PEN: "Pendiente",
  ENP: "En Proceso",
  RES: "Resuelta",
  REC: "Rechazada",
};

export const ESTADO_OPCIONES: { value: EstadoQuejaCode; label: string }[] = [
  { value: "PEN", label: "Pendiente" },
  { value: "ENP", label: "En Proceso" },
  { value: "RES", label: "Resuelta" },
  { value: "REC", label: "Rechazada" },
];
