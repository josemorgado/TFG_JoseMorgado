export type ListState<TFilters, TSort extends string = string>={
    filters: TFilters;
    sortBy: TSort;
    isFiltersOpen: boolean;
    isSortOpen: boolean;
}