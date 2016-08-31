betasmartz.AutoLogoutModal = function (urls) {
    var $elem = $("#sessionExpiresModal"),
        showWhenSecondsLeft = 60,
        self = this,

        time = {
            _expiresAt: null,

            get expiresAt() {
                if (this._expiresAt == null) {
                    this.expiresAt = $elem.data("sessionExpiresAt");
                }
                return this._expiresAt;
            },
            set expiresAt(dateString) {
                if (dateString) {
                    this._expiresAt = new Date(dateString);
                }
            },

            get secondsLeft() {
                if (this.expiresAt) {
                    return Math.floor((this.expiresAt - new Date()) / 1000)
                }
            }
        },

        timer = {
            _updateTimer: undefined,
            _logoutTimer: undefined,

            on: function () {
                if (this._updateTimer == undefined) {
                    this._updateTimer = setInterval(setTime, 1000);
                    this._logoutTimer = setTimeout(logout, time.secondsLeft * 1000);
                } else {
                    console.error('Attempted to enable working timer!');
                }
            },

            off: function () {
                if (this._updateTimer) {
                    this._updateTimer = clearTimeout(this._updateTimer);
                } else {
                    console.error('Attempted to shutdown disabled timer!');
                }
                if (this._logoutTimer) {
                    clearTimeout(this._logoutTimer);
                }
            }
        },

        keepAliveUrl = urls.keepAliveUrl,
        logoutUrl = urls.logoutUrl;

    function setTime() {
        $elem.find(".time-left").html(time.secondsLeft);
    }

    function logout() {
        window.location = logoutUrl;
    }

    this.init = function () {
        if (time.secondsLeft) {
            setTimeout(function () {
                setTime();
                $elem.modal('show');
            }, (time.secondsLeft - showWhenSecondsLeft + 1) * 1000);
        }
    };
    this.updateExpirationTime = function (dateString) {
        time.expiresAt = dateString;
        self.init();
    };

    $elem
        .find(".stay-logged-in").click(function () {
            $.get(keepAliveUrl, function (r) {
                expiresAt = new Date(r.meta.session_expires_on);
                $elem.data("sessionExpiresAt", r.meta.session_expires_on);
            });
        }).end()

        .find(".do-logout").click(logout).end()

        .on('hidden.bs.modal', timer.off)
        .on('show.bs.modal', timer.on);
};
