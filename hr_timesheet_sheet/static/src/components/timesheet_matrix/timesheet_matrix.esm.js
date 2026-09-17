import {X2Many2DMatrixRenderer} from "@web_widget_x2many_2d_matrix/components/x2many_2d_matrix_renderer/x2many_2d_matrix_renderer.esm";
import {patch} from "@web/core/utils/patch";

patch(X2Many2DMatrixRenderer.prototype, {
    _getColumns(records) {
        const columns = super._getColumns(...arguments);
        const today = luxon.DateTime.now().toISODate();
        const allRecords = records || this.list.records;

        for (const col of columns) {
            const record = allRecords.find((r) => {
                const val = r.data[this.matrixFields.x];
                return (Array.isArray(val) ? val[0] : val) === col.value;
            });

            if (record?.data?.date) {
                const dateStr =
                    record.data.date.toISODate?.() || record.data.date.split(" ")[0];
                col.isToday = dateStr === today;
            }
        }
        return columns;
    },

    _getCellClass(column, rowValue) {
        const x = this.columns.findIndex((c) => c.value === column.value);
        const y = this.rows.findIndex((r) => r.value === rowValue);
        const val = this.matrix[y]?.[x]?.value || 0;
        return {
            o_matrix_today: column.isToday,
            o_matrix_value_nonzero: val > 0,
            o_matrix_value_zero: val === 0,
        };
    },

    _getColumnTotalClass(column) {
        return {o_matrix_today: column.isToday};
    },
});
