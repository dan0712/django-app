betasmartz.AutoLogoutModal = function (urls) {
    var $elem = $("#sessionExpiresModal"),
        expiresAt = $elem.data("sessionExpiresAt"),
        showWhenSecondsLeft = 60,
        secondsLeft,
        self = this,
        updateTimer = null,

        keepAliveUrl = urls.keepAliveUrl,
        logoutUrl = urls.logoutUrl;

    this.init = function () {
        if (secondsLeft) {
            setTimeout(function () {
                $elem.modal('show');
            }, (secondsLeft - showWhenSecondsLeft) * 1000);
        }
    };
    this.setTime = function () {
        secondsLeft = Math.floor((new Date(expiresAt) - (new Date())) / 1000);
        $elem.find(".time-left").html(secondsLeft);
    };
    this.countdownOn = function () {
        if (updateTimer == null) {
            updateTimer = setInterval(self.setTime, 1000);
        } else {
            console.error('Attempted to enable working timer!');
        }
    };
    this.countdownOff = function () {
        if (updateTimer) {
            clearTimeout(updateTimer);
        } else {
            console.error('Attempted to shutdown disabled timer!');
        }
    };

    $elem.find(".stay-logged-in").click(function () {
        $.get(keepAliveUrl, function (r) {
            expiresAt = new Date(r.meta.session_expires_on);
            $elem.data("sessionExpiresAt", r.meta.session_expires_on);
        });
    });
    $elem.find(".do-logout").click(function () {
        window.location = logoutUrl;
    });

    if (expiresAt) {
        this.setTime();

        $elem.on('hidden.bs.modal', function () {
            self.countdownOff();
        });
        $elem.on('show.bs.modal', function () {
            self.countdownOn();
        })
    }
};
