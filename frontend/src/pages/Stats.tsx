import { useEffect, useMemo, useState } from "react";
import {
    getTopCategorias,
    getTopDistritos,
    getEstados,
    getOverview,
    getTimeSeries,
} from "../api/stats";

import type {
    DistritoStats,
    CategoriaStats,
    Overview,
    EstadosDistrib,
    TimePoint,
    StatsParams,
    EstadoCode,
} from "../api/stats";

import "../styles/Stats.css";

import { useCategorias, useDistritos } from "../modules/catalogos/catalogos.queries";

import {
    ResponsiveContainer,
    PieChart,
    Pie,
    Cell,
    Tooltip,
    Legend,
    BarChart,
    Bar,
    XAxis,
    YAxis,
    CartesianGrid,
    LineChart,
    Line,
    AreaChart,
    Area,
    Brush,
    Sector,
} from "recharts";


// ===========================
// Tipos
// ===========================
type GroupBy = "day" | "week" | "month" | "year";

interface Filters extends Omit<StatsParams, "limit" | "ordering" | "include_zero"> { }

const STATE_LABELS: Record<EstadoCode, string> = {
    PEN: "Pendiente",
    ENP: "En Progreso",
    RES: "Resuelta",
    REC: "Rechazada",
};

const ESTADOS_OPTIONS: { value: EstadoCode; label: string }[] = [
    { value: "PEN", label: "Pendiente" },
    { value: "ENP", label: "En Progreso" },
    { value: "RES", label: "Resuelta" },
    { value: "REC", label: "Rechazada" },
];

function splitEstados(value?: string): EstadoCode[] {
    if (!value) return [];
    return value
        .split(",")
        .map(s => s.trim())
        .filter(Boolean) as EstadoCode[];
}

function joinEstados(values: EstadoCode[]): string | undefined {
    return values.length ? values.join(", ") : undefined;
}

const COLORS = [
    "var(--color-primary)",
    "var(--color-secondary)",
    "#2E90FA",
    "#12B76A",
    "#F79009",
    "#F04438",
    "#9E77ED",
    "#7CD4FD",
];


// ===========================
// COMPONENTE PRINCIPAL
// ===========================
export default function Stats() {

    // --- Cargar catálogos ---
    const {
        data: categoriasCat,
        isLoading: catLoading,
        error: catError,
    } = useCategorias();

    const {
        data: distritosCat,
        isLoading: disLoading,
        error: disError,
    } = useDistritos();


    // ---------- Filtros ----------
    const [filters, setFilters] = useState<Filters>({
        user_id: undefined,
        desde: undefined,
        hasta: undefined,
        estado: undefined,
        categoria_id: undefined,
        distrito_id: undefined,
    });

    const [groupBy, setGroupBy] = useState<GroupBy>("month");
    const [stackByEstado, setStackByEstado] = useState<boolean>(false);

    // Ranking params
    const [limitCategorias, setLimitCategorias] = useState<number>(0);
    const [orderingCategorias, setOrderingCategorias] =
        useState<"-total" | "total" | "nombre">("-total");
    const [includeZeroCategorias, setIncludeZeroCategorias] =
        useState<boolean>(false);

    const [limitDistritos, setLimitDistritos] = useState<number>(0);
    const [orderingDistritos, setOrderingDistritos] =
        useState<"-total" | "total" | "nombre">("-total");
    const [includeZeroDistritos, setIncludeZeroDistritos] =
        useState<boolean>(false);


    // ---------- Datos ----------
    const [loading, setLoading] = useState<boolean>(true);
    const [overview, setOverview] = useState<Overview | null>(null);
    const [estados, setEstados] = useState<EstadosDistrib | null>(null);
    const [categorias, setCategorias] = useState<CategoriaStats[]>([]);
    const [distritos, setDistritos] = useState<DistritoStats[]>([]);
    const [series, setSeries] = useState<TimePoint[]>([]);
    const [error, setError] = useState<string | null>(null);


    // ---------- Parámetros derivados ----------
    const paramsCategorias = useMemo(
        () => ({
            ...filters,
            limit: limitCategorias,
            ordering: orderingCategorias,
            include_zero: includeZeroCategorias,
        }),
        [filters, limitCategorias, orderingCategorias, includeZeroCategorias]
    );

    const paramsDistritos = useMemo(
        () => ({
            ...filters,
            limit: limitDistritos,
            ordering: orderingDistritos,
            include_zero: includeZeroDistritos,
        }),
        [filters, limitDistritos, orderingDistritos, includeZeroDistritos]
    );

    const paramsGlobales = useMemo(() => ({ ...filters }), [filters]);

    const paramsSeries = useMemo(
        () => ({
            ...filters,
            group_by: groupBy,
            stack_by: stackByEstado ? ("estado" as const) : ("none" as const),
        }),
        [filters, groupBy, stackByEstado]
    );


    // ---------- Cargar datos ----------
    useEffect(() => {
        let cancel = false;

        async function fetchAll() {
            try {
                setLoading(true);
                setError(null);

                const [
                    overviewRes,
                    estadosRes,
                    categoriasRes,
                    distritosRes,
                    seriesRes,
                ] = await Promise.all([
                    getOverview(paramsGlobales),
                    getEstados(paramsGlobales),
                    getTopCategorias(paramsCategorias),
                    getTopDistritos(paramsDistritos),
                    getTimeSeries(paramsSeries),
                ]);

                if (cancel) return;

                setOverview(overviewRes);
                setEstados(estadosRes);
                setCategorias(categoriasRes);
                setDistritos(distritosRes);
                setSeries(seriesRes);

            } catch (err: any) {
                if (cancel) return;
                setError(err?.response?.data?.detail || "Error al cargar estadísticas");
            } finally {
                if (!cancel) setLoading(false);
            }
        }

        fetchAll();
        return () => { cancel = true; };
    }, [paramsGlobales, paramsCategorias, paramsDistritos, paramsSeries]);


    // ---------- Acciones ----------
    const applyFilterCategoria = (id?: number) =>
        setFilters((f) => ({ ...f, categoria_id: id }));

    const applyFilterDistrito = (id?: number) =>
        setFilters((f) => ({ ...f, distrito_id: id }));

    const applyFilterEstado = (code?: EstadoCode) =>
        setFilters((f) => ({ ...f, estado: code || undefined }));

    const resetAll = () => {
        setFilters({
            user_id: undefined,
            desde: undefined,
            hasta: undefined,
            estado: undefined,
            categoria_id: undefined,
            distrito_id: undefined,
        });

        setGroupBy("month");
        setStackByEstado(false);

        setLimitCategorias(5);
        setOrderingCategorias("-total");
        setIncludeZeroCategorias(false);

        setLimitDistritos(5);
        setOrderingDistritos("-total");
        setIncludeZeroDistritos(false);
    };


    // ===========================
    // RENDER
    // ===========================
    return (
        <div className="stats-container">

            <h2 style={{ margin: 0, color: "var(--color-primary)" }}>
                Estadísticas de quejas
            </h2>

            <div className="stats-filters card" style={{ marginTop: 12 }}>
                <FiltersForm
                    value={filters}
                    onChange={setFilters}
                    onReset={resetAll}
                    catalogos={{
                        categorias: categoriasCat ?? [],
                        distritos: distritosCat ?? [],
                        loading: catLoading || disLoading,
                        error: catError || disError,
                    }}
                    maxCategorias={categoriasCat?.length ?? 0}
                    maxDistritos={distritosCat?.length ?? 0}
                    rankingControls={{
                        categorias: {
                            limit: limitCategorias,
                            ordering: orderingCategorias,
                            includeZero: includeZeroCategorias,
                            setLimit: setLimitCategorias,
                            setOrdering: setOrderingCategorias,
                            setIncludeZero: setIncludeZeroCategorias,
                        },
                        distritos: {
                            limit: limitDistritos,
                            ordering: orderingDistritos,
                            includeZero: includeZeroDistritos,
                            setLimit: setLimitDistritos,
                            setOrdering: setOrderingDistritos,
                            setIncludeZero: setIncludeZeroDistritos,
                        },
                    }}
                    timeControls={{
                        groupBy,
                        setGroupBy,
                        stackByEstado,
                        setStackByEstado,
                    }}
                />
            </div>

            {error && (
                <div className="card" style={{
                    border: "2px solid var(--color-danger)",
                    color: "var(--color-danger)",
                }}>
                    {error}
                </div>
            )}

            {/* KPIs */}
            <div className="kpi-grid">
                <KPI label="Total" value={overview?.total ?? 0} />
                <KPI label="Pendientes" value={overview?.pen ?? 0} />
                <KPI label="En progreso" value={overview?.enp ?? 0} />
                <KPI label="Resueltas" value={overview?.res ?? 0} />
            </div>

            {/* Gráficos */}
            <div className="stats-grid">

                <div className="chart-card">
                    <h3 className="chart-title">Quejas por categoría</h3>
                    {loading ? <Skeleton /> : (
                        <CategoriasChart
                            data={categorias}
                            onClickItem={(id) => applyFilterCategoria(id)}
                        />
                    )}
                </div>

                <div className="chart-card">
                    <h3 className="chart-title">Quejas por distrito</h3>
                    {loading ? <Skeleton /> : (
                        <DistritosChart
                            data={distritos}
                            onClickItem={(id) => applyFilterDistrito(id)}
                        />
                    )}
                </div>

                <div className="chart-card card-3">
                    <h3 className="chart-title">Por estado</h3>
                    {loading ? <Skeleton /> : (
                        <EstadosDonut
                            data={estados}
                            onClickEstado={(c) => applyFilterEstado(c)}
                        />
                    )}
                </div>

                <div className="chart-card chart-card--full">
                    <div className="evolucion-temporal">
                        <h3 className="chart-title">Evolución temporal</h3>

                        <div className="chart-stack">
                            <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                                <input
                                    type="checkbox"
                                    checked={stackByEstado}
                                    onChange={(e) => setStackByEstado(e.target.checked)}
                                />
                                <span>Stacked</span>
                            </div>
                        </div>
                    </div>
                    {loading ? <Skeleton /> : (
                        <TimeSeriesChart data={series} stacked={stackByEstado} />
                    )}

                </div>
            </div>

        </div>
    );
}



// ===========================
// SUBCOMPONENTES
// ===========================
function KPI({ label, value }: { label: string; value: number }) {
    return (
        <div className="kpi-card">
            <p className="kpi-value">{value}</p>
            <p className="kpi-label">{label}</p>
        </div>
    );
}

function Skeleton() {
    return (
        <div
            style={{
                height: 240,
                background: "rgba(0,0,0,0.05)",
                borderRadius: "var(--radius)",
            }}
        />
    );
}



// ===========================
// FORMULARIO DE FILTROS
// ===========================
type FiltersFormProps = {
    value: Filters;
    onChange: (f: Filters) => void;
    onReset: () => void;
    catalogos: {
        categorias: { id: number; nombre: string }[];
        distritos: { id: number; nombre: string }[];
        loading: boolean;
        error: any;
    };
    rankingControls: any;
    timeControls: any;
    maxCategorias: number;
    maxDistritos: number;

};

function FiltersForm({
    value,
    onChange,
    onReset,
    catalogos,
    rankingControls,
    timeControls,
    maxCategorias,
    maxDistritos,
}: FiltersFormProps) {

    const setField = (k: keyof Filters, v: any) =>
        onChange({ ...value, [k]: v || undefined });

    return (
        <>
            <div className="filters-grid">

                <div>
                    <label>Desde</label>
                    <input className="input" type="date"
                        value={value.desde || ""}
                        onChange={(e) => setField("desde", e.target.value)} />
                </div>

                <div>
                    <label>Hasta</label>
                    <input className="input" type="date"
                        value={value.hasta || ""}
                        onChange={(e) => setField("hasta", e.target.value)} />
                </div>

                <div>
                    <label>Categoría</label>
                    <select
                        className="input"
                        value={value.categoria_id ?? ""}
                        disabled={catalogos.loading}
                        onChange={(e) =>
                            setField("categoria_id", e.target.value ? Number(e.target.value) : undefined)}
                    >
                        <option value="">Todas</option>
                        {catalogos.categorias?.map((c) => (
                            <option key={c.id} value={c.id}>{c.nombre}</option>
                        ))}
                    </select>
                </div>

                <div>
                    <label>Distrito</label>
                    <select
                        className="input"
                        value={value.distrito_id ?? ""}
                        disabled={catalogos.loading}
                        onChange={(e) =>
                            setField("distrito_id", e.target.value ? Number(e.target.value) : undefined)}
                    >
                        <option value="">Todos</option>
                        {catalogos.distritos?.map((d) => (
                            <option key={d.id} value={d.id}>{d.nombre}</option>
                        ))}
                    </select>
                </div>


                <div>
                    <label>Estados</label>
                    <select
                        className="input"
                        multiple
                        value={splitEstados(value.estado)}
                        title="Para seleccionar varios usar CTRL"
                        onChange={(e) => {
                            const selected = Array.from(e.target.selectedOptions).map(
                                (o) => o.value as EstadoCode
                            );
                            setField("estado", joinEstados(selected));
                        }}
                    >
                        {ESTADOS_OPTIONS.map((opt) => (
                            <option key={opt.value} value={opt.value}>
                                {opt.label}
                            </option>
                        ))}
                    </select>
                </div>


                <div>
                    <label>Solo mis quejas (user_id)</label>
                    <input
                        className="input"
                        type="number"
                        value={value.user_id ?? ""}
                        onChange={(e) =>
                            setField("user_id", e.target.value ? Number(e.target.value) : undefined)}
                    />
                </div>

                {/* Ranking categorias */}
                <div>
                    <label>Top categorías</label>
                    <div style={{ display: "flex", gap: 8 }}>
                        <input
                            className="input"
                            type="number"
                            min={0}
                            max={maxCategorias}
                            value={rankingControls.categorias.limit}
                            onChange={(e) =>
                                rankingControls.categorias.setLimit(Number(e.target.value || 5))}
                            style={{ width: 70 }}
                        />

                    </div>
                </div>

                {/* Ranking distritos */}
                <div>
                    <label>Top distritos</label>
                    <div style={{ display: "flex", gap: 8 }}>
                        <input
                            className="input"
                            type="number"
                            min={0}
                            max={maxDistritos}
                            value={rankingControls.distritos.limit}
                            onChange={(e) =>
                                rankingControls.distritos.setLimit(Number(e.target.value || 5))}
                            style={{ width: 70 }}
                        />
                    </div>
                </div>

                {/* Serie temporal */}
                <div>
                    <label>Granularidad</label>
                    <select
                        className="input"
                        value={timeControls.groupBy}
                        onChange={(e) => timeControls.setGroupBy(e.target.value as GroupBy)}
                    >
                        <option value="day">día</option>
                        <option value="week">semana</option>
                        <option value="month">mes</option>
                        <option value="year">año</option>
                    </select>
                </div>

                <div className="filters-actions">
                    <button className="btn btn-secondary" onClick={() => onReset()}>
                        Restablecer
                    </button>
                </div>
            </div>
        </>
    );
}



// ===========================
// GRÁFICOS
// ===========================

// ---- CATEGORIAS ----
function CategoriasChart({
    data,
    onClickItem,
}: {
    data: CategoriaStats[];
    onClickItem: (id?: number) => void;
}) {

    const useBars = data.length > 10;

    if (useBars) {
        const prepared = [...data].sort((a, b) => b.total - a.total);

        return (
            <ResponsiveContainer width="100%" height={280}>
                <BarChart data={prepared} margin={{ top: 8, right: 8, left: 8, bottom: 24 }}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="nombre" angle={-20} textAnchor="end" height={50} />
                    <YAxis allowDecimals={false} />
                    <Tooltip />
                    <Bar
                        dataKey="total"
                        fill="var(--color-primary)"
                        radius={[6, 6, 0, 0]}
                        onClick={(_, idx) => onClickItem(prepared[idx]?.id)}
                    />
                </BarChart>
            </ResponsiveContainer>
        );
    }

    return (
        <ResponsiveContainer width="100%" height={280}>
            <PieChart>
                <Pie
                    data={data}
                    dataKey="total"
                    nameKey="nombre"
                    innerRadius={60}
                    outerRadius={100}
                    paddingAngle={2}
                    onClick={(_, idx) => onClickItem(data[idx]?.id)}
                    shape={(props) => (
                        <Sector
                            {...props}
                            fill={COLORS[(props.index ?? 0) % COLORS.length]}
                        />
                    )}
                >
                    {data.map((_, idx) => (
                        <Cell key={idx} fill={COLORS[idx % COLORS.length]} />
                    ))}
                </Pie>
                <Tooltip />
                <Legend />
            </PieChart>
        </ResponsiveContainer>
    );
}



// ---- DISTRITOS ----
function DistritosChart({
    data,
    onClickItem,
}: {
    data: DistritoStats[];
    onClickItem: (id?: number) => void;
}) {

    const useBars = data.length > 10;

    if (useBars) {
        const prepared = [...data].sort((a, b) => b.total - a.total);

        return (
            <ResponsiveContainer width="100%" height={280}>
                <BarChart data={prepared} margin={{ top: 8, right: 8, left: 8, bottom: 24 }}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="nombre" angle={-20} textAnchor="end" height={50} />
                    <YAxis allowDecimals={false} />
                    <Tooltip />
                    <Bar
                        dataKey="total"
                        fill="var(--color-secondary)"
                        radius={[6, 6, 0, 0]}
                        onClick={(_, idx) => onClickItem(prepared[idx]?.id)}
                    />
                </BarChart>
            </ResponsiveContainer>
        );
    }

    return (
        <ResponsiveContainer width="100%" height={280}>
            <PieChart>
                <Pie
                    data={data}
                    dataKey="total"
                    nameKey="nombre"
                    innerRadius={60}
                    outerRadius={100}
                    paddingAngle={2}
                    onClick={(_, idx) => onClickItem(data[idx]?.id)}
                    shape={(props) => (
                        <Sector
                            {...props}
                            fill={COLORS[(props.index ?? 0) % COLORS.length]}
                        />
                    )}
                >
                    {data.map((_, idx) => (
                        <Cell key={idx} fill={COLORS[idx % COLORS.length]} />
                    ))}
                </Pie>
                <Tooltip />
                <Legend />
            </PieChart>
        </ResponsiveContainer>
    );
}



// ---- ESTADOS ----
function EstadosDonut({
    data,
    onClickEstado,
}: {
    data: EstadosDistrib | null;
    onClickEstado: (c?: EstadoCode) => void;
}) {

    if (!data) return null;

    const items: { name: string, code: EstadoCode, value: number }[] = [
        { name: STATE_LABELS.PEN, code: "PEN", value: data.PEN },
        { name: STATE_LABELS.ENP, code: "ENP", value: data.ENP },
        { name: STATE_LABELS.RES, code: "RES", value: data.RES },
        { name: STATE_LABELS.REC, code: "REC", value: data.REC },
    ];

    return (
        <ResponsiveContainer width="100%" height={280}>
            <PieChart>

                <Pie
                    data={items}
                    dataKey="value"
                    nameKey="name"
                    innerRadius={60}
                    outerRadius={100}
                    paddingAngle={2}
                    onClick={(_, idx) => onClickEstado(items[idx].code)}
                    shape={(props) => (
                        <Sector {...props} fill={COLORS[(props.index ?? 0) % COLORS.length]} />
                    )}
                >
                    {items.map((_, idx) => (
                        <Cell key={idx} fill={COLORS[idx % COLORS.length]} />
                    ))}
                </Pie>
                <Legend />
            </PieChart>
        </ResponsiveContainer>
    );
}



// ---- SERIE TEMPORAL ----
function TimeSeriesChart({
    data,
    stacked,
}: {
    data: TimePoint[];
    stacked: boolean;
}) {

    if (!data?.length) return <div>No hay datos para el rango elegido.</div>;

    if (stacked) {
        return (
            <ResponsiveContainer width="100%" height={320}>
                <AreaChart data={data} margin={{ top: 8, right: 16, left: 0, bottom: 8 }}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="period" />
                    <YAxis allowDecimals={false} />
                    <Tooltip />
                    <Legend />

                    <Area type="monotone" dataKey="by_estado.PEN" name="Pendiente"
                        stackId="1" stroke="var(--color-primary)"
                        fill="var(--color-primary)" fillOpacity={0.35} />

                    <Area type="monotone" dataKey="by_estado.ENP" name="En Progreso"
                        stackId="1" stroke="#2E90FA"
                        fill="#2E90FA" fillOpacity={0.35} />

                    <Area type="monotone" dataKey="by_estado.RES" name="Resuelta"
                        stackId="1" stroke="#12B76A"
                        fill="#12B76A" fillOpacity={0.35} />

                    <Area type="monotone" dataKey="by_estado.REC" name="Rechazada"
                        stackId="1" stroke="#F04438"
                        fill="#F04438" fillOpacity={0.35} />

                    <Brush dataKey="period" height={18} stroke="var(--color-primary)" />

                </AreaChart>
            </ResponsiveContainer>
        );
    }

    return (
        <ResponsiveContainer width="100%" height={320}>
            <LineChart data={data} margin={{ top: 8, right: 16, left: 0, bottom: 8 }}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="period" />
                <YAxis allowDecimals={false} />
                <Tooltip />
                <Legend />
                <Line
                    type="monotone"
                    dataKey="total"
                    name="Total"
                    stroke="var(--color-primary)"
                    strokeWidth={2}
                    dot={false}
                />
                <Brush dataKey="period" height={18} stroke="var(--color-primary)" />
            </LineChart>
        </ResponsiveContainer>
    );
}