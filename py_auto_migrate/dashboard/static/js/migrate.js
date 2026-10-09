document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("migrateForm");
    const sourceSelect = document.getElementById("source");
    const targetSelect = document.getElementById("target");
    const tableSelect = document.getElementById("table");
    const loadTablesButton = document.getElementById("loadTables");
    const tableLoadStatus = document.getElementById("tableLoadStatus");

    const DATABASES = {
        mysql: { fields: ["host", "port", "db_name", "username", "password"], required: ["host", "port", "db_name", "username", "password"], defaults: { port: "3306" } },
        mariadb: { fields: ["host", "port", "db_name", "username", "password"], required: ["host", "port", "db_name", "username", "password"], defaults: { port: "3306" } },
        postgresql: { fields: ["host", "port", "db_name", "username", "password"], required: ["host", "port", "db_name", "username", "password"], defaults: { port: "5432" } },
        mssql: { fields: ["host", "port", "db_name", "username", "password"], required: ["host", "port", "db_name"], defaults: { port: "1433" } },
        mongodb: { fields: ["host", "port", "db_name", "username", "password"], required: ["host", "port", "db_name"], defaults: { port: "27017" } },
        redis: { fields: ["host", "port", "db_name", "password"], required: ["host", "port"], defaults: { port: "6379", db_name: "0" } },
        clickhouse: { fields: ["host", "port", "db_name", "username", "password"], required: ["host", "port", "db_name"], defaults: { port: "9000", username: "default" } },
        oracle: { fields: ["host", "port", "username", "password", "service_name"], required: ["host", "port", "username", "password", "service_name"], defaults: { port: "1521" } },
        dynamodb: { fields: ["aws_access_key", "aws_secret_key", "host", "port", "region"], required: ["aws_access_key", "aws_secret_key", "host", "port", "region"], defaults: { port: "8000", region: "us-east-1" } },
        elasticsearch: { fields: ["host", "port", "username", "password"], required: ["host", "port"], defaults: { port: "9200" } },
        sqlite: { fields: ["file_path"], required: ["file_path"] }
    };
    const LABELS = { mysql: "MySQL", mariadb: "MariaDB", postgresql: "PostgreSQL", mongodb: "MongoDB", mssql: "SQL Server", redis: "Redis", clickhouse: "ClickHouse", oracle: "Oracle", dynamodb: "DynamoDB", elasticsearch: "Elasticsearch", sqlite: "SQLite" };
    const AI_DATABASES = new Set(["mysql", "mariadb", "postgresql", "mssql", "oracle", "sqlite", "clickhouse"]);

    document.querySelectorAll("#source option, #target option").forEach(option => {
        if (LABELS[option.value]) option.textContent = LABELS[option.value];
    });

    function updateSide(side, select, hintId) {
        const db = select.value.toLowerCase();
        const config = DATABASES[db];
        const hint = document.getElementById(hintId);
        document.querySelectorAll(`.field-${side}`).forEach(wrapper => {
            const field = wrapper.className.split(/\s+/).find(name => name.startsWith("field-") && name !== `field-${side}`)?.slice(6);
            const visible = Boolean(config && config.fields.includes(field));
            wrapper.hidden = !visible;
            const input = wrapper.querySelector("input");
            if (!input) return;
            input.required = visible && config.required.includes(field);
            if (visible && config.defaults?.[field] && !input.value) input.value = config.defaults[field];
        });
        if (hint) hint.textContent = config
            ? `${LABELS[db] || db}: fill in the required connection details${config.fields.some(f => !config.required.includes(f)) ? "; credentials are optional where supported" : ""}.`
            : "Select a database to see the fields needed to connect.";
    }

    function updateAI() {
        const supported = AI_DATABASES.has(targetSelect.value.toLowerCase());
        document.getElementById("aiSupportHint").textContent = supported
            ? "Optional. Describe a SQL query to run against the destination."
            : "Choose a supported relational destination to enable this option.";
        document.getElementById("ai_ask").disabled = !supported;
        document.getElementById("ai_model").disabled = !supported;
    }

    function resetTables(message = "Load the source list to choose individual tables or collections.") {
        tableSelect.replaceChildren(new Option("All tables and collections", ""));
        tableLoadStatus.textContent = message;
    }

    sourceSelect.addEventListener("change", () => {
        updateSide("s", sourceSelect, "sourceHint");
        resetTables();
    });
    targetSelect.addEventListener("change", () => {
        updateSide("t", targetSelect, "targetHint");
        updateAI();
    });
    updateSide("s", sourceSelect, "sourceHint");
    updateSide("t", targetSelect, "targetHint");
    updateAI();

    loadTablesButton.addEventListener("click", async () => {
        if (!sourceSelect.value) {
            sourceSelect.focus();
            tableLoadStatus.textContent = "Select a source database first.";
            return;
        }
        const sourceFields = [...document.querySelectorAll(".field-s input[required]")];
        const invalid = sourceFields.find(input => !input.checkValidity());
        if (invalid) {
            invalid.reportValidity();
            return;
        }
        loadTablesButton.disabled = true;
        loadTablesButton.querySelector("span").textContent = "Loading…";
        tableLoadStatus.textContent = "Connecting to source…";
        try {
            const response = await fetch("/migrate/tables", { method: "POST", body: new FormData(form) });
            const result = await response.json();
            if (!response.ok || !result.success) throw new Error(result.message || "Could not load table list");
            const previous = tableSelect.value;
            tableSelect.replaceChildren(new Option("All tables and collections", ""));
            result.tables.forEach(name => tableSelect.add(new Option(name, name)));
            if (result.tables.includes(previous)) tableSelect.value = previous;
            tableLoadStatus.textContent = `${result.tables.length} ${result.tables.length === 1 ? "table or collection" : "tables and collections"} loaded.`;
        } catch (error) {
            resetTables(`Could not load tables: ${error.message}`);
        } finally {
            loadTablesButton.disabled = false;
            loadTablesButton.querySelector("span").textContent = "Load list";
        }
    });

    const progressPanel = document.getElementById("migrationProgress");
    const progressBar = document.getElementById("progressBar");
    const progressPercent = document.getElementById("progressPercent");
    const progressStatus = document.getElementById("progressStatus");
    const progressRows = document.getElementById("progressRows");
    const migrationSummary = document.getElementById("migrationSummary");
    const submitButton = document.getElementById("startMigration");
    let isSubmitting = false;

    function renderSummary(summary) {
        migrationSummary.hidden = false;
        document.getElementById("summaryTables").textContent =
            `Tables: ${summary.tables_succeeded} succeeded, ${summary.tables_failed} failed, ${summary.tables_empty} empty, ${summary.tables_already_present} already up to date (${summary.tables_total} total)`;
        document.getElementById("summaryRows").textContent =
            `Rows: ${summary.rows_read} read, ${summary.rows_submitted} submitted, ${summary.rows_skipped_existing} already present`;
        const issues = document.getElementById("summaryIssues");
        issues.replaceChildren();
        summary.table_results.filter(row => row.status === "failed" || row.status === "empty").forEach(row => {
            const item = document.createElement("li");
            item.textContent = row.status === "failed" ? `${row.table}: ${row.error}` : `${row.table}: no rows returned from source`;
            issues.appendChild(item);
        });
    }

    function updateProgress(status) {
        const percent = Math.min(100, Math.max(0, Number(status.percent || 0)));
        progressBar.style.width = `${percent}%`;
        progressBar.textContent = `${percent.toFixed(1)}%`;
        progressPercent.textContent = `${percent.toFixed(1)}%`;
        progressBar.parentElement.setAttribute("aria-valuenow", String(Math.round(percent)));
        if (status.current_table) {
            progressStatus.textContent = `Migrating ${status.current_table}`;
            progressRows.textContent = `${status.current_table_processed} / ${status.current_table_total} rows` +
                (status.total_tables ? ` · table ${status.current_table_index} / ${status.total_tables}` : "");
        }
        if (["completed", "completed_with_errors"].includes(status.status)) {
            progressBar.classList.remove("progress-bar-animated");
            progressStatus.textContent = status.status === "completed" ? "Migration completed" : "Migration completed with errors";
            submitButton.disabled = false;
            if (status.summary) renderSummary(status.summary);
        } else if (status.status === "failed") {
            progressBar.classList.remove("progress-bar-animated");
            progressBar.classList.add("bg-danger");
            progressStatus.textContent = status.error_message || "Migration failed";
            submitButton.disabled = false;
        }
    }

    async function pollProgress(jobId) {
        const response = await fetch(`/migrate/status/${jobId}`);
        const status = await response.json();
        if (!response.ok) throw new Error(status.message || "Unable to read migration status");
        updateProgress(status);
        if (!["completed", "completed_with_errors", "failed"].includes(status.status)) {
            window.setTimeout(() => pollProgress(jobId).catch(showError), 500);
        }
    }

    function showError(error) {
        progressStatus.textContent = error.message || "Migration failed";
        progressBar.classList.remove("progress-bar-animated");
        progressBar.classList.add("bg-danger");
        submitButton.disabled = false;
    }

    form.addEventListener("submit", async event => {
        event.preventDefault();
        if (isSubmitting) return;
        const invalid = [...form.querySelectorAll("[required]")].find(input => !input.disabled && !input.checkValidity());
        if (invalid) { invalid.reportValidity(); return; }
        isSubmitting = true;
        progressPanel.hidden = false;
        progressStatus.textContent = "Starting migration…";
        progressRows.textContent = "";
        migrationSummary.hidden = true;
        document.getElementById("summaryIssues").replaceChildren();
        progressBar.classList.remove("bg-danger");
        progressBar.classList.add("progress-bar-animated");
        submitButton.disabled = true;
        try {
            const response = await fetch(form.action, { method: "POST", body: new FormData(form) });
            const result = await response.json();
            if (!response.ok || !result.success) throw new Error(result.message || "Unable to start migration");
            await pollProgress(result.job_id);
        } catch (error) { showError(error); }
        finally { isSubmitting = false; }
    });
});
