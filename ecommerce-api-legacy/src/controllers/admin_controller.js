const reportModel = require('../models/report_model');

function createAdminController(db) {
    async function financialReport(req, res, next) {
        try {
            const rows = await reportModel.getFinancialReportRows(db);
            const reportByCourse = new Map();

            for (const row of rows) {
                if (!reportByCourse.has(row.course_id)) {
                    reportByCourse.set(row.course_id, {
                        course: row.course_title,
                        revenue: 0,
                        students: [],
                    });
                }

                if (row.student_name === null) {
                    continue;
                }

                const courseData = reportByCourse.get(row.course_id);

                if (row.payment_status === 'PAID') {
                    courseData.revenue += row.payment_amount;
                }

                courseData.students.push({
                    student: row.student_name || 'Unknown',
                    paid: row.payment_amount || 0,
                });
            }

            return res.json(Array.from(reportByCourse.values()));
        } catch (err) {
            return next(err);
        }
    }

    return { financialReport };
}

module.exports = { createAdminController };
