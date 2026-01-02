export async function read_global_var(filepath, varname) {
    const file = await fetch(filepath);
    let data = await file.body.getReader().read();
    data = new TextDecoder().decode(data.value);
    data = data.split(/\n/);

    let multi = false;
    let mtxt = false;

    for (let line of data) {
        if (multi) {
            if (line.trimEnd().endsWith(multi)) {
                mtxt += '\n' + line.trimEnd().slice(0, -3);
                return mtxt;
            }
            else {
                mtxt += '\n' + line;
            }
        }
        else if (line.startsWith(varname)) {
            line = line.slice(varname.length);
            if (/^ *=/.test(line)) {
                line = line.slice(line.indexOf('=')+1).trimStart();
                const quote = line.charAt(0);
                if (quote == '"' || quote == "'") {
                    if (line.charAt(1) == quote && line.charAt(2) == quote) {
                        multi = quote + quote + quote;
                        line = line.slice(3);
                        mtxt = line;
                    }
                    else {
                        line = line.trimEnd();
                        if (line.endsWith(quote)) {
                            line = line.slice(1, -1);
                            return line;
                        }
                    }
                }
            }
        }
    }
}

