
function ScholarshipFilters({ filters, setFilters, onApply, onClear }) {
  const handleChange = (event) => {
    const { name, value } = event.target;

    setFilters((previousFilters) => ({
      ...previousFilters,
      [name]: value,
    }));
  };

  return (
    <aside className="scholarship-filters">
      <div className="filter-heading">
        <h2>Filters</h2>
        <button type="button" onClick={onClear}>
          Clear All
        </button>
      </div>

      <form
        onSubmit={(event) => {
          event.preventDefault();
          onApply();
        }}
      >
        <div className="filter-group">
          <label htmlFor="category">Category</label>
          <input
            id="category"
            name="category"
            type="text"
            placeholder="Enter category"
            value={filters.category}
            onChange={handleChange}
          />
        </div>

        <div className="filter-group">
          <label htmlFor="state">State</label>
          <input
            id="state"
            name="state"
            type="text"
            placeholder="Enter state"
            value={filters.state}
            onChange={handleChange}
          />
        </div>

        <div className="filter-group">
          <label htmlFor="course">Course</label>
          <input
            id="course"
            name="course"
            type="text"
            placeholder="Enter course"
            value={filters.course}
            onChange={handleChange}
          />
        </div>

        <div className="filter-group">
          <label htmlFor="min_amount">Minimum Amount</label>
          <input
            id="min_amount"
            name="min_amount"
            type="number"
            min="0"
            placeholder="Enter minimum amount"
            value={filters.min_amount}
            onChange={handleChange}
          />
        </div>

        <button type="submit" className="apply-filters-btn">
          Apply Filters
        </button>
      </form>
    </aside>
  );
}

export default ScholarshipFilters;
