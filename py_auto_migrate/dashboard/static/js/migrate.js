
document.addEventListener("DOMContentLoaded", function () {

    const sourceSelect = document.getElementById("source");
    const targetSelect = document.getElementById("target");

    const DB_CONFIG = {
        postgresql: ["host","port","db_name","table","username","password"],
        mysql: ["host","port","db_name","table","username","password"],
        mariadb: ["host","port","db_name","table","username","password"],
        mongodb: ["host","port","db_name","table","username","password"],
        mssql: ["host","port","db_name","table","username","password"],
        redis: ["host","port","db_name","table","username","password"],
        clickhouse: ["host","port","db_name","table","username","password"],
        oracle: ["host","port","username","password","service_name","table"],

        dynamodb: ["aws_access_key","aws_secret_key","host","port","region"],
        elasticsearch: ["host","port","username","password"],
        sqlite: ["file_path"]
    };

    function update(){

        const s = sourceSelect.value.toLowerCase();
        const t = targetSelect.value.toLowerCase();

        const sFields = DB_CONFIG[s] || [];
        const tFields = DB_CONFIG[t] || [];

        document.querySelectorAll(".field-s").forEach(el => el.style.display = "none");
        document.querySelectorAll(".field-t").forEach(el => el.style.display = "none");

        sFields.forEach(f => {
            const el = document.querySelector(`.field-s.field-${f}`);
            if(el) el.style.display = "block";
        });

        tFields.forEach(f => {
            const el = document.querySelector(`.field-t.field-${f}`);
            if(el) el.style.display = "block";
        });
    }

    sourceSelect.addEventListener("change", update);
    targetSelect.addEventListener("change", update);

    update();
});