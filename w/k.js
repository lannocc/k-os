const PREAMBLE = '::K-OS::';
const PORT = 42981
const WAIT_RECONNECT = 981; // milliseconds

let status_text = '';
let status_class = '';

let pws = null; // python websocket
let connecting = true;
const on_message = new Map();

function pws_connect() {
    const proto = window.location.protocol == 'https:' ? 'wss:' : 'ws:';
    let url = proto+'//'+window.location.hostname;
    if (window.location.protocol != 'https:') url += ':'+PORT;
    status_text = 'CONNECTING '+url;
    status_class = 'connecting';
    const status = document.getElementById('pws');
    if (status) {
        status.innerHTML = status_text;
        status.className = status_class;
    }

    pws = new WebSocket(url);

    pws.addEventListener('open', (event) => {
        status_text = 'ONLINE';
        status_class = 'online';
        const status = document.getElementById('pws');
        if (status) {
            status.innerHTML = status_text;
            status.className = status_class;
        }
        connecting = false;
    });

    pws.addEventListener('close', async (event) => {
        console.error(event);
        if (connecting) {
            status_text = 'FAILED ' + status_text;
            status_class = 'error';
        }
        else {
            status_text = 'DISCONNECTED';
            status_class = '';
        }

        const status = document.getElementById('pws');
        if (status) {
            status.innerHTML = status_text;
            status.className = status_class;
        }

        connecting = true;
        setTimeout(() => {
            status_text = 'RETRYING '+url;
            status_class = 'retrying';
            if (status) {
                status.innerHTML = status_text;
                status.className = status_class;
            }
            setTimeout(pws_connect, WAIT_RECONNECT / 2);
        }, WAIT_RECONNECT / 2);
    });

    pws.addEventListener('message', async (event) => {
        if (!on_message.size) {
            console.log('ignoring', event);
            return;
        }

        const sorted = new Map([...on_message].sort((a, b) => a[0] - b[0]));
        let common = false;
        if (sorted.has(0)) {
            common = sorted.get(0);
            sorted.delete(0);
        }

        const data = JSON.parse(event.data);
        let done = false;

        for (const [ slot, callback ] of sorted.entries()) {
            done = await callback(data);
            if (done) break;
        }

        if (!done && common) {
            await common(data);
        }
    });
}

async function pws_send(data) {
    const msg = PREAMBLE + JSON.stringify(data);

    if (connecting) {
        async function waitForConnect() {
            function waitForIt() {
                if (! connecting) return;
                return new Promise((resolve) => setTimeout(resolve, 100))
                    .then(() => Promise.resolve())
                    .then(() => waitForIt());
            }
            return waitForIt();
        }

        await waitForConnect();
    }

    pws.send(msg);
}

window.k_on_message = (callback, slot) => {
    if (slot) {
        if (!Number.isInteger(slot)) {
            console.error('slot must be integer', slot);
            return;
        }
    }
    else slot = 0;
    on_message.set(slot, callback);
}

window.k_status = () => {
    return [ status_text, status_class ];
};

window.k_reset = (reason) => {
    if (reason) pws.close(4209, reason);
    else pws.close();
};

window.k_call = async (module, data) => {
    if (data === undefined) data = { };
    req = { };
    req[module] = data;
    return pws_send(req);
};

BigInt.prototype.toJSON = function () {
    return this.toString();
}


pws_connect(); // connect automatically on script (page) load

