let socket = io({transports: ['websocket'], upgrade: false});
let shouldSubscribe = false;
let shouldWarn = true;
socket.on('disconnect', function () {
    const el = document.getElementById("disconnected");
    shouldWarn && el && (el.style['display'] = 'block');
});
socket.on('connect', function () {
    const el = document.getElementById("disconnected");
    shouldWarn && el && (el.style['display'] = 'none');
    if (shouldSubscribe) {
        socket.emit('subscribe');
    }
});