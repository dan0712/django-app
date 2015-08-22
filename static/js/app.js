if (function(t, e) {
        "object" == typeof module && "object" == typeof module.exports ? module.exports = t.document ? e(t, !0) : function(t) {
            if (!t.document) throw new Error("jQuery requires a window with a document");
            return e(t)
        } : e(t)
    }("undefined" != typeof window ? window : this, function(t, e) {
        function n(t) {
            var e = t.length,
                n = ie.type(t);
            return "function" === n || ie.isWindow(t) ? !1 : 1 === t.nodeType && e ? !0 : "array" === n || 0 === e || "number" == typeof e && e > 0 && e - 1 in t
        }

        function r(t, e, n) {
            if (ie.isFunction(e)) return ie.grep(t, function(t, r) {
                return !!e.call(t, r, t) !== n
            });
            if (e.nodeType) return ie.grep(t, function(t) {
                return t === e !== n
            });
            if ("string" == typeof e) {
                if (de.test(e)) return ie.filter(e, t, n);
                e = ie.filter(e, t)
            }
            return ie.grep(t, function(t) {
                return ie.inArray(t, e) >= 0 !== n
            })
        }

        function i(t, e) {
            do t = t[e]; while (t && 1 !== t.nodeType);
            return t
        }

        function o(t) {
            var e = we[t] = {};
            return ie.each(t.match(be) || [], function(t, n) {
                e[n] = !0
            }), e
        }

        function a() {
            he.addEventListener ? (he.removeEventListener("DOMContentLoaded", s, !1), t.removeEventListener("load", s, !1)) : (he.detachEvent("onreadystatechange", s), t.detachEvent("onload", s))
        }

        function s() {
            (he.addEventListener || "load" === event.type || "complete" === he.readyState) && (a(), ie.ready())
        }

        function u(t, e, n) {
            if (void 0 === n && 1 === t.nodeType) {
                var r = "data-" + e.replace(Te, "-$1").toLowerCase();
                if (n = t.getAttribute(r), "string" == typeof n) {
                    try {
                        n = "true" === n ? !0 : "false" === n ? !1 : "null" === n ? null : +n + "" === n ? +n : ke.test(n) ? ie.parseJSON(n) : n
                    } catch (i) {}
                    ie.data(t, e, n)
                } else n = void 0
            }
            return n
        }

        function l(t) {
            var e;
            for (e in t)
                if (("data" !== e || !ie.isEmptyObject(t[e])) && "toJSON" !== e) return !1;
            return !0
        }

        function c(t, e, n, r) {
            if (ie.acceptData(t)) {
                var i, o, a = ie.expando,
                    s = t.nodeType,
                    u = s ? ie.cache : t,
                    l = s ? t[a] : t[a] && a;
                if (l && u[l] && (r || u[l].data) || void 0 !== n || "string" != typeof e) return l || (l = s ? t[a] = X.pop() || ie.guid++ : a), u[l] || (u[l] = s ? {} : {
                    toJSON: ie.noop
                }), ("object" == typeof e || "function" == typeof e) && (r ? u[l] = ie.extend(u[l], e) : u[l].data = ie.extend(u[l].data, e)), o = u[l], r || (o.data || (o.data = {}), o = o.data), void 0 !== n && (o[ie.camelCase(e)] = n), "string" == typeof e ? (i = o[e], null == i && (i = o[ie.camelCase(e)])) : i = o, i
            }
        }

        function f(t, e, n) {
            if (ie.acceptData(t)) {
                var r, i, o = t.nodeType,
                    a = o ? ie.cache : t,
                    s = o ? t[ie.expando] : ie.expando;
                if (a[s]) {
                    if (e && (r = n ? a[s] : a[s].data)) {
                        ie.isArray(e) ? e = e.concat(ie.map(e, ie.camelCase)) : e in r ? e = [e] : (e = ie.camelCase(e), e = e in r ? [e] : e.split(" ")), i = e.length;
                        for (; i--;) delete r[e[i]];
                        if (n ? !l(r) : !ie.isEmptyObject(r)) return
                    }(n || (delete a[s].data, l(a[s]))) && (o ? ie.cleanData([t], !0) : ne.deleteExpando || a != a.window ? delete a[s] : a[s] = null)
                }
            }
        }

        function d() {
            return !0
        }

        function p() {
            return !1
        }

        function h() {
            try {
                return he.activeElement
            } catch (t) {}
        }

        function g(t) {
            var e = Fe.split("|"),
                n = t.createDocumentFragment();
            if (n.createElement)
                for (; e.length;) n.createElement(e.pop());
            return n
        }

        function m(t, e) {
            var n, r, i = 0,
                o = typeof t.getElementsByTagName !== Ce ? t.getElementsByTagName(e || "*") : typeof t.querySelectorAll !== Ce ? t.querySelectorAll(e || "*") : void 0;
            if (!o)
                for (o = [], n = t.childNodes || t; null != (r = n[i]); i++) !e || ie.nodeName(r, e) ? o.push(r) : ie.merge(o, m(r, e));
            return void 0 === e || e && ie.nodeName(t, e) ? ie.merge([t], o) : o
        }

        function v(t) {
            Ae.test(t.type) && (t.defaultChecked = t.checked)
        }

        function y(t, e) {
            return ie.nodeName(t, "table") && ie.nodeName(11 !== e.nodeType ? e : e.firstChild, "tr") ? t.getElementsByTagName("tbody")[0] || t.appendChild(t.ownerDocument.createElement("tbody")) : t
        }

        function b(t) {
            return t.type = (null !== ie.find.attr(t, "type")) + "/" + t.type, t
        }

        function w(t) {
            var e = Ke.exec(t.type);
            return e ? t.type = e[1] : t.removeAttribute("type"), t
        }

        function x(t, e) {
            for (var n, r = 0; null != (n = t[r]); r++) ie._data(n, "globalEval", !e || ie._data(e[r], "globalEval"))
        }

        function _(t, e) {
            if (1 === e.nodeType && ie.hasData(t)) {
                var n, r, i, o = ie._data(t),
                    a = ie._data(e, o),
                    s = o.events;
                if (s) {
                    delete a.handle, a.events = {};
                    for (n in s)
                        for (r = 0, i = s[n].length; i > r; r++) ie.event.add(e, n, s[n][r])
                }
                a.data && (a.data = ie.extend({}, a.data))
            }
        }

        function C(t, e) {
            var n, r, i;
            if (1 === e.nodeType) {
                if (n = e.nodeName.toLowerCase(), !ne.noCloneEvent && e[ie.expando]) {
                    i = ie._data(e);
                    for (r in i.events) ie.removeEvent(e, r, i.handle);
                    e.removeAttribute(ie.expando)
                }
                "script" === n && e.text !== t.text ? (b(e).text = t.text, w(e)) : "object" === n ? (e.parentNode && (e.outerHTML = t.outerHTML), ne.html5Clone && t.innerHTML && !ie.trim(e.innerHTML) && (e.innerHTML = t.innerHTML)) : "input" === n && Ae.test(t.type) ? (e.defaultChecked = e.checked = t.checked, e.value !== t.value && (e.value = t.value)) : "option" === n ? e.defaultSelected = e.selected = t.defaultSelected : ("input" === n || "textarea" === n) && (e.defaultValue = t.defaultValue)
            }
        }

        function k(e, n) {
            var r, i = ie(n.createElement(e)).appendTo(n.body),
                o = t.getDefaultComputedStyle && (r = t.getDefaultComputedStyle(i[0])) ? r.display : ie.css(i[0], "display");
            return i.detach(), o
        }

        function T(t) {
            var e = he,
                n = Ye[t];
            return n || (n = k(t, e), "none" !== n && n || (Ze = (Ze || ie("<iframe frameborder='0' width='0' height='0'/>")).appendTo(e.documentElement), e = (Ze[0].contentWindow || Ze[0].contentDocument).document, e.write(), e.close(), n = k(t, e), Ze.detach()), Ye[t] = n), n
        }

        function S(t, e) {
            return {
                get: function() {
                    var n = t();
                    if (null != n) return n ? void delete this.get : (this.get = e).apply(this, arguments)
                }
            }
        }

        function j(t, e) {
            if (e in t) return e;
            for (var n = e.charAt(0).toUpperCase() + e.slice(1), r = e, i = pn.length; i--;)
                if (e = pn[i] + n, e in t) return e;
            return r
        }

        function E(t, e) {
            for (var n, r, i, o = [], a = 0, s = t.length; s > a; a++) r = t[a], r.style && (o[a] = ie._data(r, "olddisplay"), n = r.style.display, e ? (o[a] || "none" !== n || (r.style.display = ""), "" === r.style.display && Ee(r) && (o[a] = ie._data(r, "olddisplay", T(r.nodeName)))) : (i = Ee(r), (n && "none" !== n || !i) && ie._data(r, "olddisplay", i ? n : ie.css(r, "display"))));
            for (a = 0; s > a; a++) r = t[a], r.style && (e && "none" !== r.style.display && "" !== r.style.display || (r.style.display = e ? o[a] || "" : "none"));
            return t
        }

        function N(t, e, n) {
            var r = ln.exec(e);
            return r ? Math.max(0, r[1] - (n || 0)) + (r[2] || "px") : e
        }

        function A(t, e, n, r, i) {
            for (var o = n === (r ? "border" : "content") ? 4 : "width" === e ? 1 : 0, a = 0; 4 > o; o += 2) "margin" === n && (a += ie.css(t, n + je[o], !0, i)), r ? ("content" === n && (a -= ie.css(t, "padding" + je[o], !0, i)), "margin" !== n && (a -= ie.css(t, "border" + je[o] + "Width", !0, i))) : (a += ie.css(t, "padding" + je[o], !0, i), "padding" !== n && (a += ie.css(t, "border" + je[o] + "Width", !0, i)));
            return a
        }

        function $(t, e, n) {
            var r = !0,
                i = "width" === e ? t.offsetWidth : t.offsetHeight,
                o = tn(t),
                a = ne.boxSizing && "border-box" === ie.css(t, "boxSizing", !1, o);
            if (0 >= i || null == i) {
                if (i = en(t, e, o), (0 > i || null == i) && (i = t.style[e]), rn.test(i)) return i;
                r = a && (ne.boxSizingReliable() || i === t.style[e]), i = parseFloat(i) || 0
            }
            return i + A(t, e, n || (a ? "border" : "content"), r, o) + "px"
        }

        function O(t, e, n, r, i) {
            return new O.prototype.init(t, e, n, r, i)
        }

        function D() {
            return setTimeout(function() {
                hn = void 0
            }), hn = ie.now()
        }

        function I(t, e) {
            var n, r = {
                    height: t
                },
                i = 0;
            for (e = e ? 1 : 0; 4 > i; i += 2 - e) n = je[i], r["margin" + n] = r["padding" + n] = t;
            return e && (r.opacity = r.width = t), r
        }

        function L(t, e, n) {
            for (var r, i = (wn[e] || []).concat(wn["*"]), o = 0, a = i.length; a > o; o++)
                if (r = i[o].call(n, e, t)) return r
        }

        function F(t, e, n) {
            var r, i, o, a, s, u, l, c, f = this,
                d = {},
                p = t.style,
                h = t.nodeType && Ee(t),
                g = ie._data(t, "fxshow");
            n.queue || (s = ie._queueHooks(t, "fx"), null == s.unqueued && (s.unqueued = 0, u = s.empty.fire, s.empty.fire = function() {
                s.unqueued || u()
            }), s.unqueued++, f.always(function() {
                f.always(function() {
                    s.unqueued--, ie.queue(t, "fx").length || s.empty.fire()
                })
            })), 1 === t.nodeType && ("height" in e || "width" in e) && (n.overflow = [p.overflow, p.overflowX, p.overflowY], l = ie.css(t, "display"), c = "none" === l ? ie._data(t, "olddisplay") || T(t.nodeName) : l, "inline" === c && "none" === ie.css(t, "float") && (ne.inlineBlockNeedsLayout && "inline" !== T(t.nodeName) ? p.zoom = 1 : p.display = "inline-block")), n.overflow && (p.overflow = "hidden", ne.shrinkWrapBlocks() || f.always(function() {
                p.overflow = n.overflow[0], p.overflowX = n.overflow[1], p.overflowY = n.overflow[2]
            }));
            for (r in e)
                if (i = e[r], mn.exec(i)) {
                    if (delete e[r], o = o || "toggle" === i, i === (h ? "hide" : "show")) {
                        if ("show" !== i || !g || void 0 === g[r]) continue;
                        h = !0
                    }
                    d[r] = g && g[r] || ie.style(t, r)
                } else l = void 0;
            if (ie.isEmptyObject(d)) "inline" === ("none" === l ? T(t.nodeName) : l) && (p.display = l);
            else {
                g ? "hidden" in g && (h = g.hidden) : g = ie._data(t, "fxshow", {}), o && (g.hidden = !h), h ? ie(t).show() : f.done(function() {
                    ie(t).hide()
                }), f.done(function() {
                    var e;
                    ie._removeData(t, "fxshow");
                    for (e in d) ie.style(t, e, d[e])
                });
                for (r in d) a = L(h ? g[r] : 0, r, f), r in g || (g[r] = a.start, h && (a.end = a.start, a.start = "width" === r || "height" === r ? 1 : 0))
            }
        }

        function R(t, e) {
            var n, r, i, o, a;
            for (n in t)
                if (r = ie.camelCase(n), i = e[r], o = t[n], ie.isArray(o) && (i = o[1], o = t[n] = o[0]), n !== r && (t[r] = o, delete t[n]), a = ie.cssHooks[r], a && "expand" in a) {
                    o = a.expand(o), delete t[r];
                    for (n in o) n in t || (t[n] = o[n], e[n] = i)
                } else e[r] = i
        }

        function q(t, e, n) {
            var r, i, o = 0,
                a = bn.length,
                s = ie.Deferred().always(function() {
                    delete u.elem
                }),
                u = function() {
                    if (i) return !1;
                    for (var e = hn || D(), n = Math.max(0, l.startTime + l.duration - e), r = n / l.duration || 0, o = 1 - r, a = 0, u = l.tweens.length; u > a; a++) l.tweens[a].run(o);
                    return s.notifyWith(t, [l, o, n]), 1 > o && u ? n : (s.resolveWith(t, [l]), !1)
                },
                l = s.promise({
                    elem: t,
                    props: ie.extend({}, e),
                    opts: ie.extend(!0, {
                        specialEasing: {}
                    }, n),
                    originalProperties: e,
                    originalOptions: n,
                    startTime: hn || D(),
                    duration: n.duration,
                    tweens: [],
                    createTween: function(e, n) {
                        var r = ie.Tween(t, l.opts, e, n, l.opts.specialEasing[e] || l.opts.easing);
                        return l.tweens.push(r), r
                    },
                    stop: function(e) {
                        var n = 0,
                            r = e ? l.tweens.length : 0;
                        if (i) return this;
                        for (i = !0; r > n; n++) l.tweens[n].run(1);
                        return e ? s.resolveWith(t, [l, e]) : s.rejectWith(t, [l, e]), this
                    }
                }),
                c = l.props;
            for (R(c, l.opts.specialEasing); a > o; o++)
                if (r = bn[o].call(l, t, c, l.opts)) return r;
            return ie.map(c, L, l), ie.isFunction(l.opts.start) && l.opts.start.call(t, l), ie.fx.timer(ie.extend(u, {
                elem: t,
                anim: l,
                queue: l.opts.queue
            })), l.progress(l.opts.progress).done(l.opts.done, l.opts.complete).fail(l.opts.fail).always(l.opts.always)
        }

        function M(t) {
            return function(e, n) {
                "string" != typeof e && (n = e, e = "*");
                var r, i = 0,
                    o = e.toLowerCase().match(be) || [];
                if (ie.isFunction(n))
                    for (; r = o[i++];) "+" === r.charAt(0) ? (r = r.slice(1) || "*", (t[r] = t[r] || []).unshift(n)) : (t[r] = t[r] || []).push(n)
            }
        }

        function P(t, e, n, r) {
            function i(s) {
                var u;
                return o[s] = !0, ie.each(t[s] || [], function(t, s) {
                    var l = s(e, n, r);
                    return "string" != typeof l || a || o[l] ? a ? !(u = l) : void 0 : (e.dataTypes.unshift(l), i(l), !1)
                }), u
            }
            var o = {},
                a = t === Wn;
            return i(e.dataTypes[0]) || !o["*"] && i("*")
        }

        function z(t, e) {
            var n, r, i = ie.ajaxSettings.flatOptions || {};
            for (r in e) void 0 !== e[r] && ((i[r] ? t : n || (n = {}))[r] = e[r]);
            return n && ie.extend(!0, t, n), t
        }

        function H(t, e, n) {
            for (var r, i, o, a, s = t.contents, u = t.dataTypes;
                "*" === u[0];) u.shift(), void 0 === i && (i = t.mimeType || e.getResponseHeader("Content-Type"));
            if (i)
                for (a in s)
                    if (s[a] && s[a].test(i)) {
                        u.unshift(a);
                        break
                    }
            if (u[0] in n) o = u[0];
            else {
                for (a in n) {
                    if (!u[0] || t.converters[a + " " + u[0]]) {
                        o = a;
                        break
                    }
                    r || (r = a)
                }
                o = o || r
            }
            return o ? (o !== u[0] && u.unshift(o), n[o]) : void 0
        }

        function B(t, e, n, r) {
            var i, o, a, s, u, l = {},
                c = t.dataTypes.slice();
            if (c[1])
                for (a in t.converters) l[a.toLowerCase()] = t.converters[a];
            for (o = c.shift(); o;)
                if (t.responseFields[o] && (n[t.responseFields[o]] = e), !u && r && t.dataFilter && (e = t.dataFilter(e, t.dataType)), u = o, o = c.shift())
                    if ("*" === o) o = u;
                    else if ("*" !== u && u !== o) {
                if (a = l[u + " " + o] || l["* " + o], !a)
                    for (i in l)
                        if (s = i.split(" "), s[1] === o && (a = l[u + " " + s[0]] || l["* " + s[0]])) {
                            a === !0 ? a = l[i] : l[i] !== !0 && (o = s[0], c.unshift(s[1]));
                            break
                        }
                if (a !== !0)
                    if (a && t["throws"]) e = a(e);
                    else try {
                        e = a(e)
                    } catch (f) {
                        return {
                            state: "parsererror",
                            error: a ? f : "No conversion from " + u + " to " + o
                        }
                    }
            }
            return {
                state: "success",
                data: e
            }
        }

        function W(t, e, n, r) {
            var i;
            if (ie.isArray(e)) ie.each(e, function(e, i) {
                n || Xn.test(t) ? r(t, i) : W(t + "[" + ("object" == typeof i ? e : "") + "]", i, n, r)
            });
            else if (n || "object" !== ie.type(e)) r(t, e);
            else
                for (i in e) W(t + "[" + i + "]", e[i], n, r)
        }

        function U() {
            try {
                return new t.XMLHttpRequest
            } catch (e) {}
        }

        function V() {
            try {
                return new t.ActiveXObject("Microsoft.XMLHTTP")
            } catch (e) {}
        }

        function K(t) {
            return ie.isWindow(t) ? t : 9 === t.nodeType ? t.defaultView || t.parentWindow : !1
        }
        var X = [],
            Q = X.slice,
            G = X.concat,
            J = X.push,
            Z = X.indexOf,
            Y = {},
            te = Y.toString,
            ee = Y.hasOwnProperty,
            ne = {},
            re = "1.11.1",
            ie = function(t, e) {
                return new ie.fn.init(t, e)
            },
            oe = /^[\s\uFEFF\xA0]+|[\s\uFEFF\xA0]+$/g,
            ae = /^-ms-/,
            se = /-([\da-z])/gi,
            ue = function(t, e) {
                return e.toUpperCase()
            };
        ie.fn = ie.prototype = {
            jquery: re,
            constructor: ie,
            selector: "",
            length: 0,
            toArray: function() {
                return Q.call(this)
            },
            get: function(t) {
                return null != t ? 0 > t ? this[t + this.length] : this[t] : Q.call(this)
            },
            pushStack: function(t) {
                var e = ie.merge(this.constructor(), t);
                return e.prevObject = this, e.context = this.context, e
            },
            each: function(t, e) {
                return ie.each(this, t, e)
            },
            map: function(t) {
                return this.pushStack(ie.map(this, function(e, n) {
                    return t.call(e, n, e)
                }))
            },
            slice: function() {
                return this.pushStack(Q.apply(this, arguments))
            },
            first: function() {
                return this.eq(0)
            },
            last: function() {
                return this.eq(-1)
            },
            eq: function(t) {
                var e = this.length,
                    n = +t + (0 > t ? e : 0);
                return this.pushStack(n >= 0 && e > n ? [this[n]] : [])
            },
            end: function() {
                return this.prevObject || this.constructor(null)
            },
            push: J,
            sort: X.sort,
            splice: X.splice
        }, ie.extend = ie.fn.extend = function() {
            var t, e, n, r, i, o, a = arguments[0] || {},
                s = 1,
                u = arguments.length,
                l = !1;
            for ("boolean" == typeof a && (l = a, a = arguments[s] || {}, s++), "object" == typeof a || ie.isFunction(a) || (a = {}), s === u && (a = this, s--); u > s; s++)
                if (null != (i = arguments[s]))
                    for (r in i) t = a[r], n = i[r], a !== n && (l && n && (ie.isPlainObject(n) || (e = ie.isArray(n))) ? (e ? (e = !1, o = t && ie.isArray(t) ? t : []) : o = t && ie.isPlainObject(t) ? t : {}, a[r] = ie.extend(l, o, n)) : void 0 !== n && (a[r] = n));
            return a
        }, ie.extend({
            expando: "jQuery" + (re + Math.random()).replace(/\D/g, ""),
            isReady: !0,
            error: function(t) {
                throw new Error(t)
            },
            noop: function() {},
            isFunction: function(t) {
                return "function" === ie.type(t)
            },
            isArray: Array.isArray || function(t) {
                return "array" === ie.type(t)
            },
            isWindow: function(t) {
                return null != t && t == t.window
            },
            isNumeric: function(t) {
                return !ie.isArray(t) && t - parseFloat(t) >= 0
            },
            isEmptyObject: function(t) {
                var e;
                for (e in t) return !1;
                return !0
            },
            isPlainObject: function(t) {
                var e;
                if (!t || "object" !== ie.type(t) || t.nodeType || ie.isWindow(t)) return !1;
                try {
                    if (t.constructor && !ee.call(t, "constructor") && !ee.call(t.constructor.prototype, "isPrototypeOf")) return !1
                } catch (n) {
                    return !1
                }
                if (ne.ownLast)
                    for (e in t) return ee.call(t, e);
                for (e in t);
                return void 0 === e || ee.call(t, e)
            },
            type: function(t) {
                return null == t ? t + "" : "object" == typeof t || "function" == typeof t ? Y[te.call(t)] || "object" : typeof t
            },
            globalEval: function(e) {
                e && ie.trim(e) && (t.execScript || function(e) {
                    t.eval.call(t, e)
                })(e)
            },
            camelCase: function(t) {
                return t.replace(ae, "ms-").replace(se, ue)
            },
            nodeName: function(t, e) {
                return t.nodeName && t.nodeName.toLowerCase() === e.toLowerCase()
            },
            each: function(t, e, r) {
                var i, o = 0,
                    a = t.length,
                    s = n(t);
                if (r) {
                    if (s)
                        for (; a > o && (i = e.apply(t[o], r), i !== !1); o++);
                    else
                        for (o in t)
                            if (i = e.apply(t[o], r), i === !1) break
                } else if (s)
                    for (; a > o && (i = e.call(t[o], o, t[o]), i !== !1); o++);
                else
                    for (o in t)
                        if (i = e.call(t[o], o, t[o]), i === !1) break; return t
            },
            trim: function(t) {
                return null == t ? "" : (t + "").replace(oe, "")
            },
            makeArray: function(t, e) {
                var r = e || [];
                return null != t && (n(Object(t)) ? ie.merge(r, "string" == typeof t ? [t] : t) : J.call(r, t)), r
            },
            inArray: function(t, e, n) {
                var r;
                if (e) {
                    if (Z) return Z.call(e, t, n);
                    for (r = e.length, n = n ? 0 > n ? Math.max(0, r + n) : n : 0; r > n; n++)
                        if (n in e && e[n] === t) return n
                }
                return -1
            },
            merge: function(t, e) {
                for (var n = +e.length, r = 0, i = t.length; n > r;) t[i++] = e[r++];
                if (n !== n)
                    for (; void 0 !== e[r];) t[i++] = e[r++];
                return t.length = i, t
            },
            grep: function(t, e, n) {
                for (var r, i = [], o = 0, a = t.length, s = !n; a > o; o++) r = !e(t[o], o), r !== s && i.push(t[o]);
                return i
            },
            map: function(t, e, r) {
                var i, o = 0,
                    a = t.length,
                    s = n(t),
                    u = [];
                if (s)
                    for (; a > o; o++) i = e(t[o], o, r), null != i && u.push(i);
                else
                    for (o in t) i = e(t[o], o, r), null != i && u.push(i);
                return G.apply([], u)
            },
            guid: 1,
            proxy: function(t, e) {
                var n, r, i;
                return "string" == typeof e && (i = t[e], e = t, t = i), ie.isFunction(t) ? (n = Q.call(arguments, 2), r = function() {
                    return t.apply(e || this, n.concat(Q.call(arguments)))
                }, r.guid = t.guid = t.guid || ie.guid++, r) : void 0
            },
            now: function() {
                return +new Date
            },
            support: ne
        }), ie.each("Boolean Number String Function Array Date RegExp Object Error".split(" "), function(t, e) {
            Y["[object " + e + "]"] = e.toLowerCase()
        });
        var le = function(t) {
            function e(t, e, n, r) {
                var i, o, a, s, u, l, f, p, h, g;
                if ((e ? e.ownerDocument || e : P) !== O && $(e), e = e || O, n = n || [], !t || "string" != typeof t) return n;
                if (1 !== (s = e.nodeType) && 9 !== s) return [];
                if (I && !r) {
                    if (i = ye.exec(t))
                        if (a = i[1]) {
                            if (9 === s) {
                                if (o = e.getElementById(a), !o || !o.parentNode) return n;
                                if (o.id === a) return n.push(o), n
                            } else if (e.ownerDocument && (o = e.ownerDocument.getElementById(a)) && q(e, o) && o.id === a) return n.push(o), n
                        } else {
                            if (i[2]) return Y.apply(n, e.getElementsByTagName(t)), n;
                            if ((a = i[3]) && x.getElementsByClassName && e.getElementsByClassName) return Y.apply(n, e.getElementsByClassName(a)), n
                        }
                    if (x.qsa && (!L || !L.test(t))) {
                        if (p = f = M, h = e, g = 9 === s && t, 1 === s && "object" !== e.nodeName.toLowerCase()) {
                            for (l = T(t), (f = e.getAttribute("id")) ? p = f.replace(we, "\\$&") : e.setAttribute("id", p), p = "[id='" + p + "'] ", u = l.length; u--;) l[u] = p + d(l[u]);
                            h = be.test(t) && c(e.parentNode) || e, g = l.join(",")
                        }
                        if (g) try {
                            return Y.apply(n, h.querySelectorAll(g)), n
                        } catch (m) {} finally {
                            f || e.removeAttribute("id")
                        }
                    }
                }
                return j(t.replace(ue, "$1"), e, n, r)
            }

            function n() {
                function t(n, r) {
                    return e.push(n + " ") > _.cacheLength && delete t[e.shift()], t[n + " "] = r
                }
                var e = [];
                return t
            }

            function r(t) {
                return t[M] = !0, t
            }

            function i(t) {
                var e = O.createElement("div");
                try {
                    return !!t(e)
                } catch (n) {
                    return !1
                } finally {
                    e.parentNode && e.parentNode.removeChild(e), e = null
                }
            }

            function o(t, e) {
                for (var n = t.split("|"), r = t.length; r--;) _.attrHandle[n[r]] = e
            }

            function a(t, e) {
                var n = e && t,
                    r = n && 1 === t.nodeType && 1 === e.nodeType && (~e.sourceIndex || X) - (~t.sourceIndex || X);
                if (r) return r;
                if (n)
                    for (; n = n.nextSibling;)
                        if (n === e) return -1;
                return t ? 1 : -1
            }

            function s(t) {
                return function(e) {
                    var n = e.nodeName.toLowerCase();
                    return "input" === n && e.type === t
                }
            }

            function u(t) {
                return function(e) {
                    var n = e.nodeName.toLowerCase();
                    return ("input" === n || "button" === n) && e.type === t
                }
            }

            function l(t) {
                return r(function(e) {
                    return e = +e, r(function(n, r) {
                        for (var i, o = t([], n.length, e), a = o.length; a--;) n[i = o[a]] && (n[i] = !(r[i] = n[i]))
                    })
                })
            }

            function c(t) {
                return t && typeof t.getElementsByTagName !== K && t
            }

            function f() {}

            function d(t) {
                for (var e = 0, n = t.length, r = ""; n > e; e++) r += t[e].value;
                return r
            }

            function p(t, e, n) {
                var r = e.dir,
                    i = n && "parentNode" === r,
                    o = H++;
                return e.first ? function(e, n, o) {
                    for (; e = e[r];)
                        if (1 === e.nodeType || i) return t(e, n, o)
                } : function(e, n, a) {
                    var s, u, l = [z, o];
                    if (a) {
                        for (; e = e[r];)
                            if ((1 === e.nodeType || i) && t(e, n, a)) return !0
                    } else
                        for (; e = e[r];)
                            if (1 === e.nodeType || i) {
                                if (u = e[M] || (e[M] = {}), (s = u[r]) && s[0] === z && s[1] === o) return l[2] = s[2];
                                if (u[r] = l, l[2] = t(e, n, a)) return !0
                            }
                }
            }

            function h(t) {
                return t.length > 1 ? function(e, n, r) {
                    for (var i = t.length; i--;)
                        if (!t[i](e, n, r)) return !1;
                    return !0
                } : t[0]
            }

            function g(t, n, r) {
                for (var i = 0, o = n.length; o > i; i++) e(t, n[i], r);
                return r
            }

            function m(t, e, n, r, i) {
                for (var o, a = [], s = 0, u = t.length, l = null != e; u > s; s++)(o = t[s]) && (!n || n(o, r, i)) && (a.push(o), l && e.push(s));
                return a
            }

            function v(t, e, n, i, o, a) {
                return i && !i[M] && (i = v(i)), o && !o[M] && (o = v(o, a)), r(function(r, a, s, u) {
                    var l, c, f, d = [],
                        p = [],
                        h = a.length,
                        v = r || g(e || "*", s.nodeType ? [s] : s, []),
                        y = !t || !r && e ? v : m(v, d, t, s, u),
                        b = n ? o || (r ? t : h || i) ? [] : a : y;
                    if (n && n(y, b, s, u), i)
                        for (l = m(b, p), i(l, [], s, u), c = l.length; c--;)(f = l[c]) && (b[p[c]] = !(y[p[c]] = f));
                    if (r) {
                        if (o || t) {
                            if (o) {
                                for (l = [], c = b.length; c--;)(f = b[c]) && l.push(y[c] = f);
                                o(null, b = [], l, u)
                            }
                            for (c = b.length; c--;)(f = b[c]) && (l = o ? ee.call(r, f) : d[c]) > -1 && (r[l] = !(a[l] = f))
                        }
                    } else b = m(b === a ? b.splice(h, b.length) : b), o ? o(null, a, b, u) : Y.apply(a, b)
                })
            }

            function y(t) {
                for (var e, n, r, i = t.length, o = _.relative[t[0].type], a = o || _.relative[" "], s = o ? 1 : 0, u = p(function(t) {
                        return t === e
                    }, a, !0), l = p(function(t) {
                        return ee.call(e, t) > -1
                    }, a, !0), c = [function(t, n, r) {
                        return !o && (r || n !== E) || ((e = n).nodeType ? u(t, n, r) : l(t, n, r))
                    }]; i > s; s++)
                    if (n = _.relative[t[s].type]) c = [p(h(c), n)];
                    else {
                        if (n = _.filter[t[s].type].apply(null, t[s].matches), n[M]) {
                            for (r = ++s; i > r && !_.relative[t[r].type]; r++);
                            return v(s > 1 && h(c), s > 1 && d(t.slice(0, s - 1).concat({
                                value: " " === t[s - 2].type ? "*" : ""
                            })).replace(ue, "$1"), n, r > s && y(t.slice(s, r)), i > r && y(t = t.slice(r)), i > r && d(t))
                        }
                        c.push(n)
                    }
                return h(c)
            }

            function b(t, n) {
                var i = n.length > 0,
                    o = t.length > 0,
                    a = function(r, a, s, u, l) {
                        var c, f, d, p = 0,
                            h = "0",
                            g = r && [],
                            v = [],
                            y = E,
                            b = r || o && _.find.TAG("*", l),
                            w = z += null == y ? 1 : Math.random() || .1,
                            x = b.length;
                        for (l && (E = a !== O && a); h !== x && null != (c = b[h]); h++) {
                            if (o && c) {
                                for (f = 0; d = t[f++];)
                                    if (d(c, a, s)) {
                                        u.push(c);
                                        break
                                    }
                                l && (z = w)
                            }
                            i && ((c = !d && c) && p--, r && g.push(c))
                        }
                        if (p += h, i && h !== p) {
                            for (f = 0; d = n[f++];) d(g, v, a, s);
                            if (r) {
                                if (p > 0)
                                    for (; h--;) g[h] || v[h] || (v[h] = J.call(u));
                                v = m(v)
                            }
                            Y.apply(u, v), l && !r && v.length > 0 && p + n.length > 1 && e.uniqueSort(u)
                        }
                        return l && (z = w, E = y), g
                    };
                return i ? r(a) : a
            }
            var w, x, _, C, k, T, S, j, E, N, A, $, O, D, I, L, F, R, q, M = "sizzle" + -new Date,
                P = t.document,
                z = 0,
                H = 0,
                B = n(),
                W = n(),
                U = n(),
                V = function(t, e) {
                    return t === e && (A = !0), 0
                },
                K = "undefined",
                X = 1 << 31,
                Q = {}.hasOwnProperty,
                G = [],
                J = G.pop,
                Z = G.push,
                Y = G.push,
                te = G.slice,
                ee = G.indexOf || function(t) {
                    for (var e = 0, n = this.length; n > e; e++)
                        if (this[e] === t) return e;
                    return -1
                },
                ne = "checked|selected|async|autofocus|autoplay|controls|defer|disabled|hidden|ismap|loop|multiple|open|readonly|required|scoped",
                re = "[\\x20\\t\\r\\n\\f]",
                ie = "(?:\\\\.|[\\w-]|[^\\x00-\\xa0])+",
                oe = ie.replace("w", "w#"),
                ae = "\\[" + re + "*(" + ie + ")(?:" + re + "*([*^$|!~]?=)" + re + "*(?:'((?:\\\\.|[^\\\\'])*)'|\"((?:\\\\.|[^\\\\\"])*)\"|(" + oe + "))|)" + re + "*\\]",
                se = ":(" + ie + ")(?:\\((('((?:\\\\.|[^\\\\'])*)'|\"((?:\\\\.|[^\\\\\"])*)\")|((?:\\\\.|[^\\\\()[\\]]|" + ae + ")*)|.*)\\)|)",
                ue = new RegExp("^" + re + "+|((?:^|[^\\\\])(?:\\\\.)*)" + re + "+$", "g"),
                le = new RegExp("^" + re + "*," + re + "*"),
                ce = new RegExp("^" + re + "*([>+~]|" + re + ")" + re + "*"),
                fe = new RegExp("=" + re + "*([^\\]'\"]*?)" + re + "*\\]", "g"),
                de = new RegExp(se),
                pe = new RegExp("^" + oe + "$"),
                he = {
                    ID: new RegExp("^#(" + ie + ")"),
                    CLASS: new RegExp("^\\.(" + ie + ")"),
                    TAG: new RegExp("^(" + ie.replace("w", "w*") + ")"),
                    ATTR: new RegExp("^" + ae),
                    PSEUDO: new RegExp("^" + se),
                    CHILD: new RegExp("^:(only|first|last|nth|nth-last)-(child|of-type)(?:\\(" + re + "*(even|odd|(([+-]|)(\\d*)n|)" + re + "*(?:([+-]|)" + re + "*(\\d+)|))" + re + "*\\)|)", "i"),
                    bool: new RegExp("^(?:" + ne + ")$", "i"),
                    needsContext: new RegExp("^" + re + "*[>+~]|:(even|odd|eq|gt|lt|nth|first|last)(?:\\(" + re + "*((?:-\\d)?\\d*)" + re + "*\\)|)(?=[^-]|$)", "i")
                },
                ge = /^(?:input|select|textarea|button)$/i,
                me = /^h\d$/i,
                ve = /^[^{]+\{\s*\[native \w/,
                ye = /^(?:#([\w-]+)|(\w+)|\.([\w-]+))$/,
                be = /[+~]/,
                we = /'|\\/g,
                xe = new RegExp("\\\\([\\da-f]{1,6}" + re + "?|(" + re + ")|.)", "ig"),
                _e = function(t, e, n) {
                    var r = "0x" + e - 65536;
                    return r !== r || n ? e : 0 > r ? String.fromCharCode(r + 65536) : String.fromCharCode(r >> 10 | 55296, 1023 & r | 56320)
                };
            try {
                Y.apply(G = te.call(P.childNodes), P.childNodes), G[P.childNodes.length].nodeType
            } catch (Ce) {
                Y = {
                    apply: G.length ? function(t, e) {
                        Z.apply(t, te.call(e))
                    } : function(t, e) {
                        for (var n = t.length, r = 0; t[n++] = e[r++];);
                        t.length = n - 1
                    }
                }
            }
            x = e.support = {}, k = e.isXML = function(t) {
                var e = t && (t.ownerDocument || t).documentElement;
                return e ? "HTML" !== e.nodeName : !1
            }, $ = e.setDocument = function(t) {
                var e, n = t ? t.ownerDocument || t : P,
                    r = n.defaultView;
                return n !== O && 9 === n.nodeType && n.documentElement ? (O = n, D = n.documentElement, I = !k(n), r && r !== r.top && (r.addEventListener ? r.addEventListener("unload", function() {
                    $()
                }, !1) : r.attachEvent && r.attachEvent("onunload", function() {
                    $()
                })), x.attributes = i(function(t) {
                    return t.className = "i", !t.getAttribute("className")
                }), x.getElementsByTagName = i(function(t) {
                    return t.appendChild(n.createComment("")), !t.getElementsByTagName("*").length
                }), x.getElementsByClassName = ve.test(n.getElementsByClassName) && i(function(t) {
                    return t.innerHTML = "<div class='a'></div><div class='a i'></div>", t.firstChild.className = "i", 2 === t.getElementsByClassName("i").length
                }), x.getById = i(function(t) {
                    return D.appendChild(t).id = M, !n.getElementsByName || !n.getElementsByName(M).length
                }), x.getById ? (_.find.ID = function(t, e) {
                    if (typeof e.getElementById !== K && I) {
                        var n = e.getElementById(t);
                        return n && n.parentNode ? [n] : []
                    }
                }, _.filter.ID = function(t) {
                    var e = t.replace(xe, _e);
                    return function(t) {
                        return t.getAttribute("id") === e
                    }
                }) : (delete _.find.ID, _.filter.ID = function(t) {
                    var e = t.replace(xe, _e);
                    return function(t) {
                        var n = typeof t.getAttributeNode !== K && t.getAttributeNode("id");
                        return n && n.value === e
                    }
                }), _.find.TAG = x.getElementsByTagName ? function(t, e) {
                    return typeof e.getElementsByTagName !== K ? e.getElementsByTagName(t) : void 0
                } : function(t, e) {
                    var n, r = [],
                        i = 0,
                        o = e.getElementsByTagName(t);
                    if ("*" === t) {
                        for (; n = o[i++];) 1 === n.nodeType && r.push(n);
                        return r
                    }
                    return o
                }, _.find.CLASS = x.getElementsByClassName && function(t, e) {
                    return typeof e.getElementsByClassName !== K && I ? e.getElementsByClassName(t) : void 0
                }, F = [], L = [], (x.qsa = ve.test(n.querySelectorAll)) && (i(function(t) {
                    t.innerHTML = "<select msallowclip=''><option selected=''></option></select>", t.querySelectorAll("[msallowclip^='']").length && L.push("[*^$]=" + re + "*(?:''|\"\")"), t.querySelectorAll("[selected]").length || L.push("\\[" + re + "*(?:value|" + ne + ")"), t.querySelectorAll(":checked").length || L.push(":checked")
                }), i(function(t) {
                    var e = n.createElement("input");
                    e.setAttribute("type", "hidden"), t.appendChild(e).setAttribute("name", "D"), t.querySelectorAll("[name=d]").length && L.push("name" + re + "*[*^$|!~]?="), t.querySelectorAll(":enabled").length || L.push(":enabled", ":disabled"), t.querySelectorAll("*,:x"), L.push(",.*:")
                })), (x.matchesSelector = ve.test(R = D.matches || D.webkitMatchesSelector || D.mozMatchesSelector || D.oMatchesSelector || D.msMatchesSelector)) && i(function(t) {
                    x.disconnectedMatch = R.call(t, "div"), R.call(t, "[s!='']:x"), F.push("!=", se)
                }), L = L.length && new RegExp(L.join("|")), F = F.length && new RegExp(F.join("|")), e = ve.test(D.compareDocumentPosition), q = e || ve.test(D.contains) ? function(t, e) {
                    var n = 9 === t.nodeType ? t.documentElement : t,
                        r = e && e.parentNode;
                    return t === r || !(!r || 1 !== r.nodeType || !(n.contains ? n.contains(r) : t.compareDocumentPosition && 16 & t.compareDocumentPosition(r)))
                } : function(t, e) {
                    if (e)
                        for (; e = e.parentNode;)
                            if (e === t) return !0;
                    return !1
                }, V = e ? function(t, e) {
                    if (t === e) return A = !0, 0;
                    var r = !t.compareDocumentPosition - !e.compareDocumentPosition;
                    return r ? r : (r = (t.ownerDocument || t) === (e.ownerDocument || e) ? t.compareDocumentPosition(e) : 1, 1 & r || !x.sortDetached && e.compareDocumentPosition(t) === r ? t === n || t.ownerDocument === P && q(P, t) ? -1 : e === n || e.ownerDocument === P && q(P, e) ? 1 : N ? ee.call(N, t) - ee.call(N, e) : 0 : 4 & r ? -1 : 1)
                } : function(t, e) {
                    if (t === e) return A = !0, 0;
                    var r, i = 0,
                        o = t.parentNode,
                        s = e.parentNode,
                        u = [t],
                        l = [e];
                    if (!o || !s) return t === n ? -1 : e === n ? 1 : o ? -1 : s ? 1 : N ? ee.call(N, t) - ee.call(N, e) : 0;
                    if (o === s) return a(t, e);
                    for (r = t; r = r.parentNode;) u.unshift(r);
                    for (r = e; r = r.parentNode;) l.unshift(r);
                    for (; u[i] === l[i];) i++;
                    return i ? a(u[i], l[i]) : u[i] === P ? -1 : l[i] === P ? 1 : 0
                }, n) : O
            }, e.matches = function(t, n) {
                return e(t, null, null, n)
            }, e.matchesSelector = function(t, n) {
                if ((t.ownerDocument || t) !== O && $(t), n = n.replace(fe, "='$1']"), !(!x.matchesSelector || !I || F && F.test(n) || L && L.test(n))) try {
                    var r = R.call(t, n);
                    if (r || x.disconnectedMatch || t.document && 11 !== t.document.nodeType) return r
                } catch (i) {}
                return e(n, O, null, [t]).length > 0
            }, e.contains = function(t, e) {
                return (t.ownerDocument || t) !== O && $(t), q(t, e)
            }, e.attr = function(t, e) {
                (t.ownerDocument || t) !== O && $(t);
                var n = _.attrHandle[e.toLowerCase()],
                    r = n && Q.call(_.attrHandle, e.toLowerCase()) ? n(t, e, !I) : void 0;
                return void 0 !== r ? r : x.attributes || !I ? t.getAttribute(e) : (r = t.getAttributeNode(e)) && r.specified ? r.value : null
            }, e.error = function(t) {
                throw new Error("Syntax error, unrecognized expression: " + t)
            }, e.uniqueSort = function(t) {
                var e, n = [],
                    r = 0,
                    i = 0;
                if (A = !x.detectDuplicates, N = !x.sortStable && t.slice(0), t.sort(V), A) {
                    for (; e = t[i++];) e === t[i] && (r = n.push(i));
                    for (; r--;) t.splice(n[r], 1)
                }
                return N = null, t
            }, C = e.getText = function(t) {
                var e, n = "",
                    r = 0,
                    i = t.nodeType;
                if (i) {
                    if (1 === i || 9 === i || 11 === i) {
                        if ("string" == typeof t.textContent) return t.textContent;
                        for (t = t.firstChild; t; t = t.nextSibling) n += C(t)
                    } else if (3 === i || 4 === i) return t.nodeValue
                } else
                    for (; e = t[r++];) n += C(e);
                return n
            }, _ = e.selectors = {
                cacheLength: 50,
                createPseudo: r,
                match: he,
                attrHandle: {},
                find: {},
                relative: {
                    ">": {
                        dir: "parentNode",
                        first: !0
                    },
                    " ": {
                        dir: "parentNode"
                    },
                    "+": {
                        dir: "previousSibling",
                        first: !0
                    },
                    "~": {
                        dir: "previousSibling"
                    }
                },
                preFilter: {
                    ATTR: function(t) {
                        return t[1] = t[1].replace(xe, _e), t[3] = (t[3] || t[4] || t[5] || "").replace(xe, _e), "~=" === t[2] && (t[3] = " " + t[3] + " "), t.slice(0, 4)
                    },
                    CHILD: function(t) {
                        return t[1] = t[1].toLowerCase(), "nth" === t[1].slice(0, 3) ? (t[3] || e.error(t[0]), t[4] = +(t[4] ? t[5] + (t[6] || 1) : 2 * ("even" === t[3] || "odd" === t[3])), t[5] = +(t[7] + t[8] || "odd" === t[3])) : t[3] && e.error(t[0]), t
                    },
                    PSEUDO: function(t) {
                        var e, n = !t[6] && t[2];
                        return he.CHILD.test(t[0]) ? null : (t[3] ? t[2] = t[4] || t[5] || "" : n && de.test(n) && (e = T(n, !0)) && (e = n.indexOf(")", n.length - e) - n.length) && (t[0] = t[0].slice(0, e), t[2] = n.slice(0, e)), t.slice(0, 3))
                    }
                },
                filter: {
                    TAG: function(t) {
                        var e = t.replace(xe, _e).toLowerCase();
                        return "*" === t ? function() {
                            return !0
                        } : function(t) {
                            return t.nodeName && t.nodeName.toLowerCase() === e
                        }
                    },
                    CLASS: function(t) {
                        var e = B[t + " "];
                        return e || (e = new RegExp("(^|" + re + ")" + t + "(" + re + "|$)")) && B(t, function(t) {
                            return e.test("string" == typeof t.className && t.className || typeof t.getAttribute !== K && t.getAttribute("class") || "")
                        })
                    },
                    ATTR: function(t, n, r) {
                        return function(i) {
                            var o = e.attr(i, t);
                            return null == o ? "!=" === n : n ? (o += "", "=" === n ? o === r : "!=" === n ? o !== r : "^=" === n ? r && 0 === o.indexOf(r) : "*=" === n ? r && o.indexOf(r) > -1 : "$=" === n ? r && o.slice(-r.length) === r : "~=" === n ? (" " + o + " ").indexOf(r) > -1 : "|=" === n ? o === r || o.slice(0, r.length + 1) === r + "-" : !1) : !0
                        }
                    },
                    CHILD: function(t, e, n, r, i) {
                        var o = "nth" !== t.slice(0, 3),
                            a = "last" !== t.slice(-4),
                            s = "of-type" === e;
                        return 1 === r && 0 === i ? function(t) {
                            return !!t.parentNode
                        } : function(e, n, u) {
                            var l, c, f, d, p, h, g = o !== a ? "nextSibling" : "previousSibling",
                                m = e.parentNode,
                                v = s && e.nodeName.toLowerCase(),
                                y = !u && !s;
                            if (m) {
                                if (o) {
                                    for (; g;) {
                                        for (f = e; f = f[g];)
                                            if (s ? f.nodeName.toLowerCase() === v : 1 === f.nodeType) return !1;
                                        h = g = "only" === t && !h && "nextSibling"
                                    }
                                    return !0
                                }
                                if (h = [a ? m.firstChild : m.lastChild], a && y) {
                                    for (c = m[M] || (m[M] = {}), l = c[t] || [], p = l[0] === z && l[1], d = l[0] === z && l[2], f = p && m.childNodes[p]; f = ++p && f && f[g] || (d = p = 0) || h.pop();)
                                        if (1 === f.nodeType && ++d && f === e) {
                                            c[t] = [z, p, d];
                                            break
                                        }
                                } else if (y && (l = (e[M] || (e[M] = {}))[t]) && l[0] === z) d = l[1];
                                else
                                    for (;
                                        (f = ++p && f && f[g] || (d = p = 0) || h.pop()) && ((s ? f.nodeName.toLowerCase() !== v : 1 !== f.nodeType) || !++d || (y && ((f[M] || (f[M] = {}))[t] = [z, d]), f !== e)););
                                return d -= i, d === r || d % r === 0 && d / r >= 0
                            }
                        }
                    },
                    PSEUDO: function(t, n) {
                        var i, o = _.pseudos[t] || _.setFilters[t.toLowerCase()] || e.error("unsupported pseudo: " + t);
                        return o[M] ? o(n) : o.length > 1 ? (i = [t, t, "", n], _.setFilters.hasOwnProperty(t.toLowerCase()) ? r(function(t, e) {
                            for (var r, i = o(t, n), a = i.length; a--;) r = ee.call(t, i[a]), t[r] = !(e[r] = i[a])
                        }) : function(t) {
                            return o(t, 0, i)
                        }) : o
                    }
                },
                pseudos: {
                    not: r(function(t) {
                        var e = [],
                            n = [],
                            i = S(t.replace(ue, "$1"));
                        return i[M] ? r(function(t, e, n, r) {
                            for (var o, a = i(t, null, r, []), s = t.length; s--;)(o = a[s]) && (t[s] = !(e[s] = o))
                        }) : function(t, r, o) {
                            return e[0] = t, i(e, null, o, n), !n.pop()
                        }
                    }),
                    has: r(function(t) {
                        return function(n) {
                            return e(t, n).length > 0
                        }
                    }),
                    contains: r(function(t) {
                        return function(e) {
                            return (e.textContent || e.innerText || C(e)).indexOf(t) > -1
                        }
                    }),
                    lang: r(function(t) {
                        return pe.test(t || "") || e.error("unsupported lang: " + t), t = t.replace(xe, _e).toLowerCase(),
                            function(e) {
                                var n;
                                do
                                    if (n = I ? e.lang : e.getAttribute("xml:lang") || e.getAttribute("lang")) return n = n.toLowerCase(), n === t || 0 === n.indexOf(t + "-");
                                while ((e = e.parentNode) && 1 === e.nodeType);
                                return !1
                            }
                    }),
                    target: function(e) {
                        var n = t.location && t.location.hash;
                        return n && n.slice(1) === e.id
                    },
                    root: function(t) {
                        return t === D
                    },
                    focus: function(t) {
                        return t === O.activeElement && (!O.hasFocus || O.hasFocus()) && !!(t.type || t.href || ~t.tabIndex)
                    },
                    enabled: function(t) {
                        return t.disabled === !1
                    },
                    disabled: function(t) {
                        return t.disabled === !0
                    },
                    checked: function(t) {
                        var e = t.nodeName.toLowerCase();
                        return "input" === e && !!t.checked || "option" === e && !!t.selected
                    },
                    selected: function(t) {
                        return t.parentNode && t.parentNode.selectedIndex, t.selected === !0
                    },
                    empty: function(t) {
                        for (t = t.firstChild; t; t = t.nextSibling)
                            if (t.nodeType < 6) return !1;
                        return !0
                    },
                    parent: function(t) {
                        return !_.pseudos.empty(t)
                    },
                    header: function(t) {
                        return me.test(t.nodeName)
                    },
                    input: function(t) {
                        return ge.test(t.nodeName)
                    },
                    button: function(t) {
                        var e = t.nodeName.toLowerCase();
                        return "input" === e && "button" === t.type || "button" === e
                    },
                    text: function(t) {
                        var e;
                        return "input" === t.nodeName.toLowerCase() && "text" === t.type && (null == (e = t.getAttribute("type")) || "text" === e.toLowerCase())
                    },
                    first: l(function() {
                        return [0]
                    }),
                    last: l(function(t, e) {
                        return [e - 1]
                    }),
                    eq: l(function(t, e, n) {
                        return [0 > n ? n + e : n]
                    }),
                    even: l(function(t, e) {
                        for (var n = 0; e > n; n += 2) t.push(n);
                        return t
                    }),
                    odd: l(function(t, e) {
                        for (var n = 1; e > n; n += 2) t.push(n);
                        return t
                    }),
                    lt: l(function(t, e, n) {
                        for (var r = 0 > n ? n + e : n; --r >= 0;) t.push(r);
                        return t
                    }),
                    gt: l(function(t, e, n) {
                        for (var r = 0 > n ? n + e : n; ++r < e;) t.push(r);
                        return t
                    })
                }
            }, _.pseudos.nth = _.pseudos.eq;
            for (w in {
                    radio: !0,
                    checkbox: !0,
                    file: !0,
                    password: !0,
                    image: !0
                }) _.pseudos[w] = s(w);
            for (w in {
                    submit: !0,
                    reset: !0
                }) _.pseudos[w] = u(w);
            return f.prototype = _.filters = _.pseudos, _.setFilters = new f, T = e.tokenize = function(t, n) {
                var r, i, o, a, s, u, l, c = W[t + " "];
                if (c) return n ? 0 : c.slice(0);
                for (s = t, u = [], l = _.preFilter; s;) {
                    (!r || (i = le.exec(s))) && (i && (s = s.slice(i[0].length) || s), u.push(o = [])), r = !1, (i = ce.exec(s)) && (r = i.shift(), o.push({
                        value: r,
                        type: i[0].replace(ue, " ")
                    }), s = s.slice(r.length));
                    for (a in _.filter) !(i = he[a].exec(s)) || l[a] && !(i = l[a](i)) || (r = i.shift(), o.push({
                        value: r,
                        type: a,
                        matches: i
                    }), s = s.slice(r.length));
                    if (!r) break
                }
                return n ? s.length : s ? e.error(t) : W(t, u).slice(0)
            }, S = e.compile = function(t, e) {
                var n, r = [],
                    i = [],
                    o = U[t + " "];
                if (!o) {
                    for (e || (e = T(t)), n = e.length; n--;) o = y(e[n]), o[M] ? r.push(o) : i.push(o);
                    o = U(t, b(i, r)), o.selector = t
                }
                return o
            }, j = e.select = function(t, e, n, r) {
                var i, o, a, s, u, l = "function" == typeof t && t,
                    f = !r && T(t = l.selector || t);
                if (n = n || [], 1 === f.length) {
                    if (o = f[0] = f[0].slice(0), o.length > 2 && "ID" === (a = o[0]).type && x.getById && 9 === e.nodeType && I && _.relative[o[1].type]) {
                        if (e = (_.find.ID(a.matches[0].replace(xe, _e), e) || [])[0], !e) return n;
                        l && (e = e.parentNode), t = t.slice(o.shift().value.length)
                    }
                    for (i = he.needsContext.test(t) ? 0 : o.length; i-- && (a = o[i], !_.relative[s = a.type]);)
                        if ((u = _.find[s]) && (r = u(a.matches[0].replace(xe, _e), be.test(o[0].type) && c(e.parentNode) || e))) {
                            if (o.splice(i, 1), t = r.length && d(o), !t) return Y.apply(n, r), n;
                            break
                        }
                }
                return (l || S(t, f))(r, e, !I, n, be.test(t) && c(e.parentNode) || e), n
            }, x.sortStable = M.split("").sort(V).join("") === M, x.detectDuplicates = !!A, $(), x.sortDetached = i(function(t) {
                return 1 & t.compareDocumentPosition(O.createElement("div"))
            }), i(function(t) {
                return t.innerHTML = "<a href='#'></a>", "#" === t.firstChild.getAttribute("href")
            }) || o("type|href|height|width", function(t, e, n) {
                return n ? void 0 : t.getAttribute(e, "type" === e.toLowerCase() ? 1 : 2)
            }), x.attributes && i(function(t) {
                return t.innerHTML = "<input/>", t.firstChild.setAttribute("value", ""), "" === t.firstChild.getAttribute("value")
            }) || o("value", function(t, e, n) {
                return n || "input" !== t.nodeName.toLowerCase() ? void 0 : t.defaultValue
            }), i(function(t) {
                return null == t.getAttribute("disabled")
            }) || o(ne, function(t, e, n) {
                var r;
                return n ? void 0 : t[e] === !0 ? e.toLowerCase() : (r = t.getAttributeNode(e)) && r.specified ? r.value : null
            }), e
        }(t);
        ie.find = le, ie.expr = le.selectors, ie.expr[":"] = ie.expr.pseudos, ie.unique = le.uniqueSort, ie.text = le.getText, ie.isXMLDoc = le.isXML, ie.contains = le.contains;
        var ce = ie.expr.match.needsContext,
            fe = /^<(\w+)\s*\/?>(?:<\/\1>|)$/,
            de = /^.[^:#\[\.,]*$/;
        ie.filter = function(t, e, n) {
            var r = e[0];
            return n && (t = ":not(" + t + ")"), 1 === e.length && 1 === r.nodeType ? ie.find.matchesSelector(r, t) ? [r] : [] : ie.find.matches(t, ie.grep(e, function(t) {
                return 1 === t.nodeType
            }))
        }, ie.fn.extend({
            find: function(t) {
                var e, n = [],
                    r = this,
                    i = r.length;
                if ("string" != typeof t) return this.pushStack(ie(t).filter(function() {
                    for (e = 0; i > e; e++)
                        if (ie.contains(r[e], this)) return !0
                }));
                for (e = 0; i > e; e++) ie.find(t, r[e], n);
                return n = this.pushStack(i > 1 ? ie.unique(n) : n), n.selector = this.selector ? this.selector + " " + t : t, n
            },
            filter: function(t) {
                return this.pushStack(r(this, t || [], !1))
            },
            not: function(t) {
                return this.pushStack(r(this, t || [], !0))
            },
            is: function(t) {
                return !!r(this, "string" == typeof t && ce.test(t) ? ie(t) : t || [], !1).length
            }
        });
        var pe, he = t.document,
            ge = /^(?:\s*(<[\w\W]+>)[^>]*|#([\w-]*))$/,
            me = ie.fn.init = function(t, e) {
                var n, r;
                if (!t) return this;
                if ("string" == typeof t) {
                    if (n = "<" === t.charAt(0) && ">" === t.charAt(t.length - 1) && t.length >= 3 ? [null, t, null] : ge.exec(t), !n || !n[1] && e) return !e || e.jquery ? (e || pe).find(t) : this.constructor(e).find(t);
                    if (n[1]) {
                        if (e = e instanceof ie ? e[0] : e, ie.merge(this, ie.parseHTML(n[1], e && e.nodeType ? e.ownerDocument || e : he, !0)), fe.test(n[1]) && ie.isPlainObject(e))
                            for (n in e) ie.isFunction(this[n]) ? this[n](e[n]) : this.attr(n, e[n]);
                        return this
                    }
                    if (r = he.getElementById(n[2]), r && r.parentNode) {
                        if (r.id !== n[2]) return pe.find(t);
                        this.length = 1, this[0] = r
                    }
                    return this.context = he, this.selector = t, this
                }
                return t.nodeType ? (this.context = this[0] = t, this.length = 1, this) : ie.isFunction(t) ? "undefined" != typeof pe.ready ? pe.ready(t) : t(ie) : (void 0 !== t.selector && (this.selector = t.selector, this.context = t.context), ie.makeArray(t, this))
            };
        me.prototype = ie.fn, pe = ie(he);
        var ve = /^(?:parents|prev(?:Until|All))/,
            ye = {
                children: !0,
                contents: !0,
                next: !0,
                prev: !0
            };
        ie.extend({
            dir: function(t, e, n) {
                for (var r = [], i = t[e]; i && 9 !== i.nodeType && (void 0 === n || 1 !== i.nodeType || !ie(i).is(n));) 1 === i.nodeType && r.push(i), i = i[e];
                return r
            },
            sibling: function(t, e) {
                for (var n = []; t; t = t.nextSibling) 1 === t.nodeType && t !== e && n.push(t);
                return n
            }
        }), ie.fn.extend({
            has: function(t) {
                var e, n = ie(t, this),
                    r = n.length;
                return this.filter(function() {
                    for (e = 0; r > e; e++)
                        if (ie.contains(this, n[e])) return !0
                })
            },
            closest: function(t, e) {
                for (var n, r = 0, i = this.length, o = [], a = ce.test(t) || "string" != typeof t ? ie(t, e || this.context) : 0; i > r; r++)
                    for (n = this[r]; n && n !== e; n = n.parentNode)
                        if (n.nodeType < 11 && (a ? a.index(n) > -1 : 1 === n.nodeType && ie.find.matchesSelector(n, t))) {
                            o.push(n);
                            break
                        }
                return this.pushStack(o.length > 1 ? ie.unique(o) : o)
            },
            index: function(t) {
                return t ? "string" == typeof t ? ie.inArray(this[0], ie(t)) : ie.inArray(t.jquery ? t[0] : t, this) : this[0] && this[0].parentNode ? this.first().prevAll().length : -1
            },
            add: function(t, e) {
                return this.pushStack(ie.unique(ie.merge(this.get(), ie(t, e))))
            },
            addBack: function(t) {
                return this.add(null == t ? this.prevObject : this.prevObject.filter(t))
            }
        }), ie.each({
            parent: function(t) {
                var e = t.parentNode;
                return e && 11 !== e.nodeType ? e : null
            },
            parents: function(t) {
                return ie.dir(t, "parentNode")
            },
            parentsUntil: function(t, e, n) {
                return ie.dir(t, "parentNode", n)
            },
            next: function(t) {
                return i(t, "nextSibling")
            },
            prev: function(t) {
                return i(t, "previousSibling")
            },
            nextAll: function(t) {
                return ie.dir(t, "nextSibling")
            },
            prevAll: function(t) {
                return ie.dir(t, "previousSibling")
            },
            nextUntil: function(t, e, n) {
                return ie.dir(t, "nextSibling", n)
            },
            prevUntil: function(t, e, n) {
                return ie.dir(t, "previousSibling", n)
            },
            siblings: function(t) {
                return ie.sibling((t.parentNode || {}).firstChild, t)
            },
            children: function(t) {
                return ie.sibling(t.firstChild)
            },
            contents: function(t) {
                return ie.nodeName(t, "iframe") ? t.contentDocument || t.contentWindow.document : ie.merge([], t.childNodes)
            }
        }, function(t, e) {
            ie.fn[t] = function(n, r) {
                var i = ie.map(this, e, n);
                return "Until" !== t.slice(-5) && (r = n), r && "string" == typeof r && (i = ie.filter(r, i)), this.length > 1 && (ye[t] || (i = ie.unique(i)), ve.test(t) && (i = i.reverse())), this.pushStack(i)
            }
        });
        var be = /\S+/g,
            we = {};
        ie.Callbacks = function(t) {
            t = "string" == typeof t ? we[t] || o(t) : ie.extend({}, t);
            var e, n, r, i, a, s, u = [],
                l = !t.once && [],
                c = function(o) {
                    for (n = t.memory && o, r = !0, a = s || 0, s = 0, i = u.length, e = !0; u && i > a; a++)
                        if (u[a].apply(o[0], o[1]) === !1 && t.stopOnFalse) {
                            n = !1;
                            break
                        }
                    e = !1, u && (l ? l.length && c(l.shift()) : n ? u = [] : f.disable())
                },
                f = {
                    add: function() {
                        if (u) {
                            var r = u.length;
                            ! function o(e) {
                                ie.each(e, function(e, n) {
                                    var r = ie.type(n);
                                    "function" === r ? t.unique && f.has(n) || u.push(n) : n && n.length && "string" !== r && o(n)
                                })
                            }(arguments), e ? i = u.length : n && (s = r, c(n))
                        }
                        return this
                    },
                    remove: function() {
                        return u && ie.each(arguments, function(t, n) {
                            for (var r;
                                (r = ie.inArray(n, u, r)) > -1;) u.splice(r, 1), e && (i >= r && i--, a >= r && a--)
                        }), this
                    },
                    has: function(t) {
                        return t ? ie.inArray(t, u) > -1 : !(!u || !u.length)
                    },
                    empty: function() {
                        return u = [], i = 0, this
                    },
                    disable: function() {
                        return u = l = n = void 0, this
                    },
                    disabled: function() {
                        return !u
                    },
                    lock: function() {
                        return l = void 0, n || f.disable(), this
                    },
                    locked: function() {
                        return !l
                    },
                    fireWith: function(t, n) {
                        return !u || r && !l || (n = n || [], n = [t, n.slice ? n.slice() : n], e ? l.push(n) : c(n)), this
                    },
                    fire: function() {
                        return f.fireWith(this, arguments), this
                    },
                    fired: function() {
                        return !!r
                    }
                };
            return f
        }, ie.extend({
            Deferred: function(t) {
                var e = [
                        ["resolve", "done", ie.Callbacks("once memory"), "resolved"],
                        ["reject", "fail", ie.Callbacks("once memory"), "rejected"],
                        ["notify", "progress", ie.Callbacks("memory")]
                    ],
                    n = "pending",
                    r = {
                        state: function() {
                            return n
                        },
                        always: function() {
                            return i.done(arguments).fail(arguments), this
                        },
                        then: function() {
                            var t = arguments;
                            return ie.Deferred(function(n) {
                                ie.each(e, function(e, o) {
                                    var a = ie.isFunction(t[e]) && t[e];
                                    i[o[1]](function() {
                                        var t = a && a.apply(this, arguments);
                                        t && ie.isFunction(t.promise) ? t.promise().done(n.resolve).fail(n.reject).progress(n.notify) : n[o[0] + "With"](this === r ? n.promise() : this, a ? [t] : arguments)
                                    })
                                }), t = null
                            }).promise()
                        },
                        promise: function(t) {
                            return null != t ? ie.extend(t, r) : r
                        }
                    },
                    i = {};
                return r.pipe = r.then, ie.each(e, function(t, o) {
                    var a = o[2],
                        s = o[3];
                    r[o[1]] = a.add, s && a.add(function() {
                        n = s
                    }, e[1 ^ t][2].disable, e[2][2].lock), i[o[0]] = function() {
                        return i[o[0] + "With"](this === i ? r : this, arguments), this
                    }, i[o[0] + "With"] = a.fireWith
                }), r.promise(i), t && t.call(i, i), i
            },
            when: function(t) {
                var e, n, r, i = 0,
                    o = Q.call(arguments),
                    a = o.length,
                    s = 1 !== a || t && ie.isFunction(t.promise) ? a : 0,
                    u = 1 === s ? t : ie.Deferred(),
                    l = function(t, n, r) {
                        return function(i) {
                            n[t] = this, r[t] = arguments.length > 1 ? Q.call(arguments) : i, r === e ? u.notifyWith(n, r) : --s || u.resolveWith(n, r)
                        }
                    };
                if (a > 1)
                    for (e = new Array(a), n = new Array(a), r = new Array(a); a > i; i++) o[i] && ie.isFunction(o[i].promise) ? o[i].promise().done(l(i, r, o)).fail(u.reject).progress(l(i, n, e)) : --s;
                return s || u.resolveWith(r, o), u.promise()
            }
        });
        var xe;
        ie.fn.ready = function(t) {
            return ie.ready.promise().done(t), this
        }, ie.extend({
            isReady: !1,
            readyWait: 1,
            holdReady: function(t) {
                t ? ie.readyWait++ : ie.ready(!0)
            },
            ready: function(t) {
                if (t === !0 ? !--ie.readyWait : !ie.isReady) {
                    if (!he.body) return setTimeout(ie.ready);
                    ie.isReady = !0, t !== !0 && --ie.readyWait > 0 || (xe.resolveWith(he, [ie]), ie.fn.triggerHandler && (ie(he).triggerHandler("ready"), ie(he).off("ready")))
                }
            }
        }), ie.ready.promise = function(e) {
            if (!xe)
                if (xe = ie.Deferred(), "complete" === he.readyState) setTimeout(ie.ready);
                else if (he.addEventListener) he.addEventListener("DOMContentLoaded", s, !1), t.addEventListener("load", s, !1);
            else {
                he.attachEvent("onreadystatechange", s), t.attachEvent("onload", s);
                var n = !1;
                try {
                    n = null == t.frameElement && he.documentElement
                } catch (r) {}
                n && n.doScroll && ! function i() {
                    if (!ie.isReady) {
                        try {
                            n.doScroll("left")
                        } catch (t) {
                            return setTimeout(i, 50)
                        }
                        a(), ie.ready()
                    }
                }()
            }
            return xe.promise(e)
        };
        var _e, Ce = "undefined";
        for (_e in ie(ne)) break;
        ne.ownLast = "0" !== _e, ne.inlineBlockNeedsLayout = !1, ie(function() {
                var t, e, n, r;
                n = he.getElementsByTagName("body")[0], n && n.style && (e = he.createElement("div"), r = he.createElement("div"), r.style.cssText = "position:absolute;border:0;width:0;height:0;top:0;left:-9999px", n.appendChild(r).appendChild(e), typeof e.style.zoom !== Ce && (e.style.cssText = "display:inline;margin:0;border:0;padding:1px;width:1px;zoom:1", ne.inlineBlockNeedsLayout = t = 3 === e.offsetWidth, t && (n.style.zoom = 1)), n.removeChild(r))
            }),
            function() {
                var t = he.createElement("div");
                if (null == ne.deleteExpando) {
                    ne.deleteExpando = !0;
                    try {
                        delete t.test
                    } catch (e) {
                        ne.deleteExpando = !1
                    }
                }
                t = null
            }(), ie.acceptData = function(t) {
                var e = ie.noData[(t.nodeName + " ").toLowerCase()],
                    n = +t.nodeType || 1;
                return 1 !== n && 9 !== n ? !1 : !e || e !== !0 && t.getAttribute("classid") === e
            };
        var ke = /^(?:\{[\w\W]*\}|\[[\w\W]*\])$/,
            Te = /([A-Z])/g;
        ie.extend({
            cache: {},
            noData: {
                "applet ": !0,
                "embed ": !0,
                "object ": "clsid:D27CDB6E-AE6D-11cf-96B8-444553540000"
            },
            hasData: function(t) {
                return t = t.nodeType ? ie.cache[t[ie.expando]] : t[ie.expando], !!t && !l(t)
            },
            data: function(t, e, n) {
                return c(t, e, n)
            },
            removeData: function(t, e) {
                return f(t, e)
            },
            _data: function(t, e, n) {
                return c(t, e, n, !0)
            },
            _removeData: function(t, e) {
                return f(t, e, !0)
            }
        }), ie.fn.extend({
            data: function(t, e) {
                var n, r, i, o = this[0],
                    a = o && o.attributes;
                if (void 0 === t) {
                    if (this.length && (i = ie.data(o), 1 === o.nodeType && !ie._data(o, "parsedAttrs"))) {
                        for (n = a.length; n--;) a[n] && (r = a[n].name, 0 === r.indexOf("data-") && (r = ie.camelCase(r.slice(5)), u(o, r, i[r])));
                        ie._data(o, "parsedAttrs", !0)
                    }
                    return i
                }
                return "object" == typeof t ? this.each(function() {
                    ie.data(this, t)
                }) : arguments.length > 1 ? this.each(function() {
                    ie.data(this, t, e)
                }) : o ? u(o, t, ie.data(o, t)) : void 0
            },
            removeData: function(t) {
                return this.each(function() {
                    ie.removeData(this, t)
                })
            }
        }), ie.extend({
            queue: function(t, e, n) {
                var r;
                return t ? (e = (e || "fx") + "queue", r = ie._data(t, e), n && (!r || ie.isArray(n) ? r = ie._data(t, e, ie.makeArray(n)) : r.push(n)), r || []) : void 0
            },
            dequeue: function(t, e) {
                e = e || "fx";
                var n = ie.queue(t, e),
                    r = n.length,
                    i = n.shift(),
                    o = ie._queueHooks(t, e),
                    a = function() {
                        ie.dequeue(t, e)
                    };
                "inprogress" === i && (i = n.shift(), r--), i && ("fx" === e && n.unshift("inprogress"), delete o.stop, i.call(t, a, o)), !r && o && o.empty.fire()
            },
            _queueHooks: function(t, e) {
                var n = e + "queueHooks";
                return ie._data(t, n) || ie._data(t, n, {
                    empty: ie.Callbacks("once memory").add(function() {
                        ie._removeData(t, e + "queue"), ie._removeData(t, n)
                    })
                })
            }
        }), ie.fn.extend({
            queue: function(t, e) {
                var n = 2;
                return "string" != typeof t && (e = t, t = "fx", n--), arguments.length < n ? ie.queue(this[0], t) : void 0 === e ? this : this.each(function() {
                    var n = ie.queue(this, t, e);
                    ie._queueHooks(this, t), "fx" === t && "inprogress" !== n[0] && ie.dequeue(this, t)
                })
            },
            dequeue: function(t) {
                return this.each(function() {
                    ie.dequeue(this, t)
                })
            },
            clearQueue: function(t) {
                return this.queue(t || "fx", [])
            },
            promise: function(t, e) {
                var n, r = 1,
                    i = ie.Deferred(),
                    o = this,
                    a = this.length,
                    s = function() {
                        --r || i.resolveWith(o, [o])
                    };
                for ("string" != typeof t && (e = t, t = void 0), t = t || "fx"; a--;) n = ie._data(o[a], t + "queueHooks"), n && n.empty && (r++, n.empty.add(s));
                return s(), i.promise(e)
            }
        });
        var Se = /[+-]?(?:\d*\.|)\d+(?:[eE][+-]?\d+|)/.source,
            je = ["Top", "Right", "Bottom", "Left"],
            Ee = function(t, e) {
                return t = e || t, "none" === ie.css(t, "display") || !ie.contains(t.ownerDocument, t)
            },
            Ne = ie.access = function(t, e, n, r, i, o, a) {
                var s = 0,
                    u = t.length,
                    l = null == n;
                if ("object" === ie.type(n)) {
                    i = !0;
                    for (s in n) ie.access(t, e, s, n[s], !0, o, a)
                } else if (void 0 !== r && (i = !0, ie.isFunction(r) || (a = !0), l && (a ? (e.call(t, r), e = null) : (l = e, e = function(t, e, n) {
                        return l.call(ie(t), n)
                    })), e))
                    for (; u > s; s++) e(t[s], n, a ? r : r.call(t[s], s, e(t[s], n)));
                return i ? t : l ? e.call(t) : u ? e(t[0], n) : o
            },
            Ae = /^(?:checkbox|radio)$/i;
        ! function() {
            var t = he.createElement("input"),
                e = he.createElement("div"),
                n = he.createDocumentFragment();
            if (e.innerHTML = "  <link/><table></table><a href='/a'>a</a><input type='checkbox'/>", ne.leadingWhitespace = 3 === e.firstChild.nodeType, ne.tbody = !e.getElementsByTagName("tbody").length, ne.htmlSerialize = !!e.getElementsByTagName("link").length, ne.html5Clone = "<:nav></:nav>" !== he.createElement("nav").cloneNode(!0).outerHTML, t.type = "checkbox", t.checked = !0, n.appendChild(t), ne.appendChecked = t.checked, e.innerHTML = "<textarea>x</textarea>", ne.noCloneChecked = !!e.cloneNode(!0).lastChild.defaultValue, n.appendChild(e), e.innerHTML = "<input type='radio' checked='checked' name='t'/>", ne.checkClone = e.cloneNode(!0).cloneNode(!0).lastChild.checked, ne.noCloneEvent = !0, e.attachEvent && (e.attachEvent("onclick", function() {
                    ne.noCloneEvent = !1
                }), e.cloneNode(!0).click()), null == ne.deleteExpando) {
                ne.deleteExpando = !0;
                try {
                    delete e.test
                } catch (r) {
                    ne.deleteExpando = !1
                }
            }
        }(),
        function() {
            var e, n, r = he.createElement("div");
            for (e in {
                    submit: !0,
                    change: !0,
                    focusin: !0
                }) n = "on" + e, (ne[e + "Bubbles"] = n in t) || (r.setAttribute(n, "t"), ne[e + "Bubbles"] = r.attributes[n].expando === !1);
            r = null
        }();
        var $e = /^(?:input|select|textarea)$/i,
            Oe = /^key/,
            De = /^(?:mouse|pointer|contextmenu)|click/,
            Ie = /^(?:focusinfocus|focusoutblur)$/,
            Le = /^([^.]*)(?:\.(.+)|)$/;
        ie.event = {
            global: {},
            add: function(t, e, n, r, i) {
                var o, a, s, u, l, c, f, d, p, h, g, m = ie._data(t);
                if (m) {
                    for (n.handler && (u = n, n = u.handler, i = u.selector), n.guid || (n.guid = ie.guid++), (a = m.events) || (a = m.events = {}), (c = m.handle) || (c = m.handle = function(t) {
                            return typeof ie === Ce || t && ie.event.triggered === t.type ? void 0 : ie.event.dispatch.apply(c.elem, arguments)
                        }, c.elem = t), e = (e || "").match(be) || [""], s = e.length; s--;) o = Le.exec(e[s]) || [], p = g = o[1], h = (o[2] || "").split(".").sort(), p && (l = ie.event.special[p] || {}, p = (i ? l.delegateType : l.bindType) || p, l = ie.event.special[p] || {}, f = ie.extend({
                        type: p,
                        origType: g,
                        data: r,
                        handler: n,
                        guid: n.guid,
                        selector: i,
                        needsContext: i && ie.expr.match.needsContext.test(i),
                        namespace: h.join(".")
                    }, u), (d = a[p]) || (d = a[p] = [], d.delegateCount = 0, l.setup && l.setup.call(t, r, h, c) !== !1 || (t.addEventListener ? t.addEventListener(p, c, !1) : t.attachEvent && t.attachEvent("on" + p, c))), l.add && (l.add.call(t, f), f.handler.guid || (f.handler.guid = n.guid)), i ? d.splice(d.delegateCount++, 0, f) : d.push(f), ie.event.global[p] = !0);
                    t = null
                }
            },
            remove: function(t, e, n, r, i) {
                var o, a, s, u, l, c, f, d, p, h, g, m = ie.hasData(t) && ie._data(t);
                if (m && (c = m.events)) {
                    for (e = (e || "").match(be) || [""], l = e.length; l--;)
                        if (s = Le.exec(e[l]) || [], p = g = s[1], h = (s[2] || "").split(".").sort(), p) {
                            for (f = ie.event.special[p] || {}, p = (r ? f.delegateType : f.bindType) || p, d = c[p] || [], s = s[2] && new RegExp("(^|\\.)" + h.join("\\.(?:.*\\.|)") + "(\\.|$)"), u = o = d.length; o--;) a = d[o], !i && g !== a.origType || n && n.guid !== a.guid || s && !s.test(a.namespace) || r && r !== a.selector && ("**" !== r || !a.selector) || (d.splice(o, 1), a.selector && d.delegateCount--, f.remove && f.remove.call(t, a));
                            u && !d.length && (f.teardown && f.teardown.call(t, h, m.handle) !== !1 || ie.removeEvent(t, p, m.handle), delete c[p])
                        } else
                            for (p in c) ie.event.remove(t, p + e[l], n, r, !0);
                    ie.isEmptyObject(c) && (delete m.handle, ie._removeData(t, "events"))
                }
            },
            trigger: function(e, n, r, i) {
                var o, a, s, u, l, c, f, d = [r || he],
                    p = ee.call(e, "type") ? e.type : e,
                    h = ee.call(e, "namespace") ? e.namespace.split(".") : [];
                if (s = c = r = r || he, 3 !== r.nodeType && 8 !== r.nodeType && !Ie.test(p + ie.event.triggered) && (p.indexOf(".") >= 0 && (h = p.split("."), p = h.shift(), h.sort()), a = p.indexOf(":") < 0 && "on" + p, e = e[ie.expando] ? e : new ie.Event(p, "object" == typeof e && e), e.isTrigger = i ? 2 : 3, e.namespace = h.join("."), e.namespace_re = e.namespace ? new RegExp("(^|\\.)" + h.join("\\.(?:.*\\.|)") + "(\\.|$)") : null, e.result = void 0, e.target || (e.target = r), n = null == n ? [e] : ie.makeArray(n, [e]), l = ie.event.special[p] || {}, i || !l.trigger || l.trigger.apply(r, n) !== !1)) {
                    if (!i && !l.noBubble && !ie.isWindow(r)) {
                        for (u = l.delegateType || p, Ie.test(u + p) || (s = s.parentNode); s; s = s.parentNode) d.push(s), c = s;
                        c === (r.ownerDocument || he) && d.push(c.defaultView || c.parentWindow || t)
                    }
                    for (f = 0;
                        (s = d[f++]) && !e.isPropagationStopped();) e.type = f > 1 ? u : l.bindType || p, o = (ie._data(s, "events") || {})[e.type] && ie._data(s, "handle"), o && o.apply(s, n), o = a && s[a], o && o.apply && ie.acceptData(s) && (e.result = o.apply(s, n), e.result === !1 && e.preventDefault());
                    if (e.type = p, !i && !e.isDefaultPrevented() && (!l._default || l._default.apply(d.pop(), n) === !1) && ie.acceptData(r) && a && r[p] && !ie.isWindow(r)) {
                        c = r[a], c && (r[a] = null), ie.event.triggered = p;
                        try {
                            r[p]()
                        } catch (g) {}
                        ie.event.triggered = void 0, c && (r[a] = c)
                    }
                    return e.result
                }
            },
            dispatch: function(t) {
                t = ie.event.fix(t);
                var e, n, r, i, o, a = [],
                    s = Q.call(arguments),
                    u = (ie._data(this, "events") || {})[t.type] || [],
                    l = ie.event.special[t.type] || {};
                if (s[0] = t, t.delegateTarget = this, !l.preDispatch || l.preDispatch.call(this, t) !== !1) {
                    for (a = ie.event.handlers.call(this, t, u), e = 0;
                        (i = a[e++]) && !t.isPropagationStopped();)
                        for (t.currentTarget = i.elem, o = 0;
                            (r = i.handlers[o++]) && !t.isImmediatePropagationStopped();)(!t.namespace_re || t.namespace_re.test(r.namespace)) && (t.handleObj = r, t.data = r.data, n = ((ie.event.special[r.origType] || {}).handle || r.handler).apply(i.elem, s), void 0 !== n && (t.result = n) === !1 && (t.preventDefault(), t.stopPropagation()));
                    return l.postDispatch && l.postDispatch.call(this, t), t.result
                }
            },
            handlers: function(t, e) {
                var n, r, i, o, a = [],
                    s = e.delegateCount,
                    u = t.target;
                if (s && u.nodeType && (!t.button || "click" !== t.type))
                    for (; u != this; u = u.parentNode || this)
                        if (1 === u.nodeType && (u.disabled !== !0 || "click" !== t.type)) {
                            for (i = [], o = 0; s > o; o++) r = e[o], n = r.selector + " ", void 0 === i[n] && (i[n] = r.needsContext ? ie(n, this).index(u) >= 0 : ie.find(n, this, null, [u]).length), i[n] && i.push(r);
                            i.length && a.push({
                                elem: u,
                                handlers: i
                            })
                        }
                return s < e.length && a.push({
                    elem: this,
                    handlers: e.slice(s)
                }), a
            },
            fix: function(t) {
                if (t[ie.expando]) return t;
                var e, n, r, i = t.type,
                    o = t,
                    a = this.fixHooks[i];
                for (a || (this.fixHooks[i] = a = De.test(i) ? this.mouseHooks : Oe.test(i) ? this.keyHooks : {}), r = a.props ? this.props.concat(a.props) : this.props, t = new ie.Event(o), e = r.length; e--;) n = r[e], t[n] = o[n];
                return t.target || (t.target = o.srcElement || he), 3 === t.target.nodeType && (t.target = t.target.parentNode), t.metaKey = !!t.metaKey, a.filter ? a.filter(t, o) : t
            },
            props: "altKey bubbles cancelable ctrlKey currentTarget eventPhase metaKey relatedTarget shiftKey target timeStamp view which".split(" "),
            fixHooks: {},
            keyHooks: {
                props: "char charCode key keyCode".split(" "),
                filter: function(t, e) {
                    return null == t.which && (t.which = null != e.charCode ? e.charCode : e.keyCode), t
                }
            },
            mouseHooks: {
                props: "button buttons clientX clientY fromElement offsetX offsetY pageX pageY screenX screenY toElement".split(" "),
                filter: function(t, e) {
                    var n, r, i, o = e.button,
                        a = e.fromElement;
                    return null == t.pageX && null != e.clientX && (r = t.target.ownerDocument || he, i = r.documentElement, n = r.body, t.pageX = e.clientX + (i && i.scrollLeft || n && n.scrollLeft || 0) - (i && i.clientLeft || n && n.clientLeft || 0), t.pageY = e.clientY + (i && i.scrollTop || n && n.scrollTop || 0) - (i && i.clientTop || n && n.clientTop || 0)), !t.relatedTarget && a && (t.relatedTarget = a === t.target ? e.toElement : a), t.which || void 0 === o || (t.which = 1 & o ? 1 : 2 & o ? 3 : 4 & o ? 2 : 0), t
                }
            },
            special: {
                load: {
                    noBubble: !0
                },
                focus: {
                    trigger: function() {
                        if (this !== h() && this.focus) try {
                            return this.focus(), !1
                        } catch (t) {}
                    },
                    delegateType: "focusin"
                },
                blur: {
                    trigger: function() {
                        return this === h() && this.blur ? (this.blur(), !1) : void 0
                    },
                    delegateType: "focusout"
                },
                click: {
                    trigger: function() {
                        return ie.nodeName(this, "input") && "checkbox" === this.type && this.click ? (this.click(), !1) : void 0
                    },
                    _default: function(t) {
                        return ie.nodeName(t.target, "a")
                    }
                },
                beforeunload: {
                    postDispatch: function(t) {
                        void 0 !== t.result && t.originalEvent && (t.originalEvent.returnValue = t.result)
                    }
                }
            },
            simulate: function(t, e, n, r) {
                var i = ie.extend(new ie.Event, n, {
                    type: t,
                    isSimulated: !0,
                    originalEvent: {}
                });
                r ? ie.event.trigger(i, null, e) : ie.event.dispatch.call(e, i), i.isDefaultPrevented() && n.preventDefault()
            }
        }, ie.removeEvent = he.removeEventListener ? function(t, e, n) {
            t.removeEventListener && t.removeEventListener(e, n, !1)
        } : function(t, e, n) {
            var r = "on" + e;
            t.detachEvent && (typeof t[r] === Ce && (t[r] = null), t.detachEvent(r, n))
        }, ie.Event = function(t, e) {
            return this instanceof ie.Event ? (t && t.type ? (this.originalEvent = t, this.type = t.type, this.isDefaultPrevented = t.defaultPrevented || void 0 === t.defaultPrevented && t.returnValue === !1 ? d : p) : this.type = t, e && ie.extend(this, e), this.timeStamp = t && t.timeStamp || ie.now(), void(this[ie.expando] = !0)) : new ie.Event(t, e)
        }, ie.Event.prototype = {
            isDefaultPrevented: p,
            isPropagationStopped: p,
            isImmediatePropagationStopped: p,
            preventDefault: function() {
                var t = this.originalEvent;
                this.isDefaultPrevented = d, t && (t.preventDefault ? t.preventDefault() : t.returnValue = !1)
            },
            stopPropagation: function() {
                var t = this.originalEvent;
                this.isPropagationStopped = d, t && (t.stopPropagation && t.stopPropagation(), t.cancelBubble = !0)
            },
            stopImmediatePropagation: function() {
                var t = this.originalEvent;
                this.isImmediatePropagationStopped = d, t && t.stopImmediatePropagation && t.stopImmediatePropagation(), this.stopPropagation()
            }
        }, ie.each({
            mouseenter: "mouseover",
            mouseleave: "mouseout",
            pointerenter: "pointerover",
            pointerleave: "pointerout"
        }, function(t, e) {
            ie.event.special[t] = {
                delegateType: e,
                bindType: e,
                handle: function(t) {
                    var n, r = this,
                        i = t.relatedTarget,
                        o = t.handleObj;
                    return (!i || i !== r && !ie.contains(r, i)) && (t.type = o.origType, n = o.handler.apply(this, arguments), t.type = e), n
                }
            }
        }), ne.submitBubbles || (ie.event.special.submit = {
            setup: function() {
                return ie.nodeName(this, "form") ? !1 : void ie.event.add(this, "click._submit keypress._submit", function(t) {
                    var e = t.target,
                        n = ie.nodeName(e, "input") || ie.nodeName(e, "button") ? e.form : void 0;
                    n && !ie._data(n, "submitBubbles") && (ie.event.add(n, "submit._submit", function(t) {
                        t._submit_bubble = !0
                    }), ie._data(n, "submitBubbles", !0))
                })
            },
            postDispatch: function(t) {
                t._submit_bubble && (delete t._submit_bubble, this.parentNode && !t.isTrigger && ie.event.simulate("submit", this.parentNode, t, !0))
            },
            teardown: function() {
                return ie.nodeName(this, "form") ? !1 : void ie.event.remove(this, "._submit")
            }
        }), ne.changeBubbles || (ie.event.special.change = {
            setup: function() {
                return $e.test(this.nodeName) ? (("checkbox" === this.type || "radio" === this.type) && (ie.event.add(this, "propertychange._change", function(t) {
                    "checked" === t.originalEvent.propertyName && (this._just_changed = !0)
                }), ie.event.add(this, "click._change", function(t) {
                    this._just_changed && !t.isTrigger && (this._just_changed = !1), ie.event.simulate("change", this, t, !0)
                })), !1) : void ie.event.add(this, "beforeactivate._change", function(t) {
                    var e = t.target;
                    $e.test(e.nodeName) && !ie._data(e, "changeBubbles") && (ie.event.add(e, "change._change", function(t) {
                        !this.parentNode || t.isSimulated || t.isTrigger || ie.event.simulate("change", this.parentNode, t, !0)
                    }), ie._data(e, "changeBubbles", !0))
                })
            },
            handle: function(t) {
                var e = t.target;
                return this !== e || t.isSimulated || t.isTrigger || "radio" !== e.type && "checkbox" !== e.type ? t.handleObj.handler.apply(this, arguments) : void 0
            },
            teardown: function() {
                return ie.event.remove(this, "._change"), !$e.test(this.nodeName)
            }
        }), ne.focusinBubbles || ie.each({
            focus: "focusin",
            blur: "focusout"
        }, function(t, e) {
            var n = function(t) {
                ie.event.simulate(e, t.target, ie.event.fix(t), !0)
            };
            ie.event.special[e] = {
                setup: function() {
                    var r = this.ownerDocument || this,
                        i = ie._data(r, e);
                    i || r.addEventListener(t, n, !0), ie._data(r, e, (i || 0) + 1)
                },
                teardown: function() {
                    var r = this.ownerDocument || this,
                        i = ie._data(r, e) - 1;
                    i ? ie._data(r, e, i) : (r.removeEventListener(t, n, !0), ie._removeData(r, e))
                }
            }
        }), ie.fn.extend({
            on: function(t, e, n, r, i) {
                var o, a;
                if ("object" == typeof t) {
                    "string" != typeof e && (n = n || e, e = void 0);
                    for (o in t) this.on(o, e, n, t[o], i);
                    return this
                }
                if (null == n && null == r ? (r = e, n = e = void 0) : null == r && ("string" == typeof e ? (r = n, n = void 0) : (r = n, n = e, e = void 0)), r === !1) r = p;
                else if (!r) return this;
                return 1 === i && (a = r, r = function(t) {
                    return ie().off(t), a.apply(this, arguments)
                }, r.guid = a.guid || (a.guid = ie.guid++)), this.each(function() {
                    ie.event.add(this, t, r, n, e)
                })
            },
            one: function(t, e, n, r) {
                return this.on(t, e, n, r, 1)
            },
            off: function(t, e, n) {
                var r, i;
                if (t && t.preventDefault && t.handleObj) return r = t.handleObj, ie(t.delegateTarget).off(r.namespace ? r.origType + "." + r.namespace : r.origType, r.selector, r.handler), this;
                if ("object" == typeof t) {
                    for (i in t) this.off(i, e, t[i]);
                    return this
                }
                return (e === !1 || "function" == typeof e) && (n = e, e = void 0), n === !1 && (n = p), this.each(function() {
                    ie.event.remove(this, t, n, e)
                })
            },
            trigger: function(t, e) {
                return this.each(function() {
                    ie.event.trigger(t, e, this)
                })
            },
            triggerHandler: function(t, e) {
                var n = this[0];
                return n ? ie.event.trigger(t, e, n, !0) : void 0
            }
        });
        var Fe = "abbr|article|aside|audio|bdi|canvas|data|datalist|details|figcaption|figure|footer|header|hgroup|mark|meter|nav|output|progress|section|summary|time|video",
            Re = / jQuery\d+="(?:null|\d+)"/g,
            qe = new RegExp("<(?:" + Fe + ")[\\s/>]", "i"),
            Me = /^\s+/,
            Pe = /<(?!area|br|col|embed|hr|img|input|link|meta|param)(([\w:]+)[^>]*)\/>/gi,
            ze = /<([\w:]+)/,
            He = /<tbody/i,
            Be = /<|&#?\w+;/,
            We = /<(?:script|style|link)/i,
            Ue = /checked\s*(?:[^=]|=\s*.checked.)/i,
            Ve = /^$|\/(?:java|ecma)script/i,
            Ke = /^true\/(.*)/,
            Xe = /^\s*<!(?:\[CDATA\[|--)|(?:\]\]|--)>\s*$/g,
            Qe = {
                option: [1, "<select multiple='multiple'>", "</select>"],
                legend: [1, "<fieldset>", "</fieldset>"],
                area: [1, "<map>", "</map>"],
                param: [1, "<object>", "</object>"],
                thead: [1, "<table>", "</table>"],
                tr: [2, "<table><tbody>", "</tbody></table>"],
                col: [2, "<table><tbody></tbody><colgroup>", "</colgroup></table>"],
                td: [3, "<table><tbody><tr>", "</tr></tbody></table>"],
                _default: ne.htmlSerialize ? [0, "", ""] : [1, "X<div>", "</div>"]
            },
            Ge = g(he),
            Je = Ge.appendChild(he.createElement("div"));
        Qe.optgroup = Qe.option, Qe.tbody = Qe.tfoot = Qe.colgroup = Qe.caption = Qe.thead, Qe.th = Qe.td, ie.extend({
            clone: function(t, e, n) {
                var r, i, o, a, s, u = ie.contains(t.ownerDocument, t);
                if (ne.html5Clone || ie.isXMLDoc(t) || !qe.test("<" + t.nodeName + ">") ? o = t.cloneNode(!0) : (Je.innerHTML = t.outerHTML, Je.removeChild(o = Je.firstChild)), !(ne.noCloneEvent && ne.noCloneChecked || 1 !== t.nodeType && 11 !== t.nodeType || ie.isXMLDoc(t)))
                    for (r = m(o), s = m(t), a = 0; null != (i = s[a]); ++a) r[a] && C(i, r[a]);
                if (e)
                    if (n)
                        for (s = s || m(t), r = r || m(o), a = 0; null != (i = s[a]); a++) _(i, r[a]);
                    else _(t, o);
                return r = m(o, "script"), r.length > 0 && x(r, !u && m(t, "script")), r = s = i = null, o
            },
            buildFragment: function(t, e, n, r) {
                for (var i, o, a, s, u, l, c, f = t.length, d = g(e), p = [], h = 0; f > h; h++)
                    if (o = t[h], o || 0 === o)
                        if ("object" === ie.type(o)) ie.merge(p, o.nodeType ? [o] : o);
                        else if (Be.test(o)) {
                    for (s = s || d.appendChild(e.createElement("div")), u = (ze.exec(o) || ["", ""])[1].toLowerCase(), c = Qe[u] || Qe._default, s.innerHTML = c[1] + o.replace(Pe, "<$1></$2>") + c[2], i = c[0]; i--;) s = s.lastChild;
                    if (!ne.leadingWhitespace && Me.test(o) && p.push(e.createTextNode(Me.exec(o)[0])), !ne.tbody)
                        for (o = "table" !== u || He.test(o) ? "<table>" !== c[1] || He.test(o) ? 0 : s : s.firstChild, i = o && o.childNodes.length; i--;) ie.nodeName(l = o.childNodes[i], "tbody") && !l.childNodes.length && o.removeChild(l);
                    for (ie.merge(p, s.childNodes), s.textContent = ""; s.firstChild;) s.removeChild(s.firstChild);
                    s = d.lastChild
                } else p.push(e.createTextNode(o));
                for (s && d.removeChild(s), ne.appendChecked || ie.grep(m(p, "input"), v), h = 0; o = p[h++];)
                    if ((!r || -1 === ie.inArray(o, r)) && (a = ie.contains(o.ownerDocument, o), s = m(d.appendChild(o), "script"), a && x(s), n))
                        for (i = 0; o = s[i++];) Ve.test(o.type || "") && n.push(o);
                return s = null, d
            },
            cleanData: function(t, e) {
                for (var n, r, i, o, a = 0, s = ie.expando, u = ie.cache, l = ne.deleteExpando, c = ie.event.special; null != (n = t[a]); a++)
                    if ((e || ie.acceptData(n)) && (i = n[s], o = i && u[i])) {
                        if (o.events)
                            for (r in o.events) c[r] ? ie.event.remove(n, r) : ie.removeEvent(n, r, o.handle);
                        u[i] && (delete u[i], l ? delete n[s] : typeof n.removeAttribute !== Ce ? n.removeAttribute(s) : n[s] = null, X.push(i))
                    }
            }
        }), ie.fn.extend({
            text: function(t) {
                return Ne(this, function(t) {
                    return void 0 === t ? ie.text(this) : this.empty().append((this[0] && this[0].ownerDocument || he).createTextNode(t))
                }, null, t, arguments.length)
            },
            append: function() {
                return this.domManip(arguments, function(t) {
                    if (1 === this.nodeType || 11 === this.nodeType || 9 === this.nodeType) {
                        var e = y(this, t);
                        e.appendChild(t)
                    }
                })
            },
            prepend: function() {
                return this.domManip(arguments, function(t) {
                    if (1 === this.nodeType || 11 === this.nodeType || 9 === this.nodeType) {
                        var e = y(this, t);
                        e.insertBefore(t, e.firstChild)
                    }
                })
            },
            before: function() {
                return this.domManip(arguments, function(t) {
                    this.parentNode && this.parentNode.insertBefore(t, this)
                })
            },
            after: function() {
                return this.domManip(arguments, function(t) {
                    this.parentNode && this.parentNode.insertBefore(t, this.nextSibling)
                })
            },
            remove: function(t, e) {
                for (var n, r = t ? ie.filter(t, this) : this, i = 0; null != (n = r[i]); i++) e || 1 !== n.nodeType || ie.cleanData(m(n)), n.parentNode && (e && ie.contains(n.ownerDocument, n) && x(m(n, "script")), n.parentNode.removeChild(n));
                return this
            },
            empty: function() {
                for (var t, e = 0; null != (t = this[e]); e++) {
                    for (1 === t.nodeType && ie.cleanData(m(t, !1)); t.firstChild;) t.removeChild(t.firstChild);
                    t.options && ie.nodeName(t, "select") && (t.options.length = 0)
                }
                return this
            },
            clone: function(t, e) {
                return t = null == t ? !1 : t, e = null == e ? t : e, this.map(function() {
                    return ie.clone(this, t, e)
                })
            },
            html: function(t) {
                return Ne(this, function(t) {
                    var e = this[0] || {},
                        n = 0,
                        r = this.length;
                    if (void 0 === t) return 1 === e.nodeType ? e.innerHTML.replace(Re, "") : void 0;
                    if (!("string" != typeof t || We.test(t) || !ne.htmlSerialize && qe.test(t) || !ne.leadingWhitespace && Me.test(t) || Qe[(ze.exec(t) || ["", ""])[1].toLowerCase()])) {
                        t = t.replace(Pe, "<$1></$2>");
                        try {
                            for (; r > n; n++) e = this[n] || {}, 1 === e.nodeType && (ie.cleanData(m(e, !1)), e.innerHTML = t);
                            e = 0
                        } catch (i) {}
                    }
                    e && this.empty().append(t)
                }, null, t, arguments.length)
            },
            replaceWith: function() {
                var t = arguments[0];
                return this.domManip(arguments, function(e) {
                    t = this.parentNode, ie.cleanData(m(this)), t && t.replaceChild(e, this)
                }), t && (t.length || t.nodeType) ? this : this.remove()
            },
            detach: function(t) {
                return this.remove(t, !0)
            },
            domManip: function(t, e) {
                t = G.apply([], t);
                var n, r, i, o, a, s, u = 0,
                    l = this.length,
                    c = this,
                    f = l - 1,
                    d = t[0],
                    p = ie.isFunction(d);
                if (p || l > 1 && "string" == typeof d && !ne.checkClone && Ue.test(d)) return this.each(function(n) {
                    var r = c.eq(n);
                    p && (t[0] = d.call(this, n, r.html())), r.domManip(t, e)
                });
                if (l && (s = ie.buildFragment(t, this[0].ownerDocument, !1, this), n = s.firstChild, 1 === s.childNodes.length && (s = n), n)) {
                    for (o = ie.map(m(s, "script"), b), i = o.length; l > u; u++) r = s, u !== f && (r = ie.clone(r, !0, !0), i && ie.merge(o, m(r, "script"))), e.call(this[u], r, u);
                    if (i)
                        for (a = o[o.length - 1].ownerDocument, ie.map(o, w), u = 0; i > u; u++) r = o[u], Ve.test(r.type || "") && !ie._data(r, "globalEval") && ie.contains(a, r) && (r.src ? ie._evalUrl && ie._evalUrl(r.src) : ie.globalEval((r.text || r.textContent || r.innerHTML || "").replace(Xe, "")));
                    s = n = null
                }
                return this
            }
        }), ie.each({
            appendTo: "append",
            prependTo: "prepend",
            insertBefore: "before",
            insertAfter: "after",
            replaceAll: "replaceWith"
        }, function(t, e) {
            ie.fn[t] = function(t) {
                for (var n, r = 0, i = [], o = ie(t), a = o.length - 1; a >= r; r++) n = r === a ? this : this.clone(!0), ie(o[r])[e](n), J.apply(i, n.get());
                return this.pushStack(i)
            }
        });
        var Ze, Ye = {};
        ! function() {
            var t;
            ne.shrinkWrapBlocks = function() {
                if (null != t) return t;
                t = !1;
                var e, n, r;
                return n = he.getElementsByTagName("body")[0], n && n.style ? (e = he.createElement("div"), r = he.createElement("div"), r.style.cssText = "position:absolute;border:0;width:0;height:0;top:0;left:-9999px", n.appendChild(r).appendChild(e), typeof e.style.zoom !== Ce && (e.style.cssText = "-webkit-box-sizing:content-box;-moz-box-sizing:content-box;box-sizing:content-box;display:block;margin:0;border:0;padding:1px;width:1px;zoom:1", e.appendChild(he.createElement("div")).style.width = "5px", t = 3 !== e.offsetWidth), n.removeChild(r), t) : void 0
            }
        }();
        var tn, en, nn = /^margin/,
            rn = new RegExp("^(" + Se + ")(?!px)[a-z%]+$", "i"),
            on = /^(top|right|bottom|left)$/;
        t.getComputedStyle ? (tn = function(t) {
                return t.ownerDocument.defaultView.getComputedStyle(t, null)
            }, en = function(t, e, n) {
                var r, i, o, a, s = t.style;
                return n = n || tn(t), a = n ? n.getPropertyValue(e) || n[e] : void 0, n && ("" !== a || ie.contains(t.ownerDocument, t) || (a = ie.style(t, e)), rn.test(a) && nn.test(e) && (r = s.width, i = s.minWidth, o = s.maxWidth, s.minWidth = s.maxWidth = s.width = a, a = n.width, s.width = r, s.minWidth = i, s.maxWidth = o)), void 0 === a ? a : a + ""
            }) : he.documentElement.currentStyle && (tn = function(t) {
                return t.currentStyle
            }, en = function(t, e, n) {
                var r, i, o, a, s = t.style;
                return n = n || tn(t), a = n ? n[e] : void 0, null == a && s && s[e] && (a = s[e]), rn.test(a) && !on.test(e) && (r = s.left, i = t.runtimeStyle, o = i && i.left, o && (i.left = t.currentStyle.left), s.left = "fontSize" === e ? "1em" : a, a = s.pixelLeft + "px", s.left = r, o && (i.left = o)), void 0 === a ? a : a + "" || "auto"
            }),
            function() {
                function e() {
                    var e, n, r, i;
                    n = he.getElementsByTagName("body")[0], n && n.style && (e = he.createElement("div"), r = he.createElement("div"), r.style.cssText = "position:absolute;border:0;width:0;height:0;top:0;left:-9999px", n.appendChild(r).appendChild(e), e.style.cssText = "-webkit-box-sizing:border-box;-moz-box-sizing:border-box;box-sizing:border-box;display:block;margin-top:1%;top:1%;border:1px;padding:1px;width:4px;position:absolute", o = a = !1, u = !0, t.getComputedStyle && (o = "1%" !== (t.getComputedStyle(e, null) || {}).top, a = "4px" === (t.getComputedStyle(e, null) || {
                        width: "4px"
                    }).width, i = e.appendChild(he.createElement("div")), i.style.cssText = e.style.cssText = "-webkit-box-sizing:content-box;-moz-box-sizing:content-box;box-sizing:content-box;display:block;margin:0;border:0;padding:0", i.style.marginRight = i.style.width = "0", e.style.width = "1px", u = !parseFloat((t.getComputedStyle(i, null) || {}).marginRight)), e.innerHTML = "<table><tr><td></td><td>t</td></tr></table>", i = e.getElementsByTagName("td"), i[0].style.cssText = "margin:0;border:0;padding:0;display:none", s = 0 === i[0].offsetHeight, s && (i[0].style.display = "", i[1].style.display = "none", s = 0 === i[0].offsetHeight), n.removeChild(r))
                }
                var n, r, i, o, a, s, u;
                n = he.createElement("div"), n.innerHTML = "  <link/><table></table><a href='/a'>a</a><input type='checkbox'/>", i = n.getElementsByTagName("a")[0], r = i && i.style, r && (r.cssText = "float:left;opacity:.5", ne.opacity = "0.5" === r.opacity, ne.cssFloat = !!r.cssFloat, n.style.backgroundClip = "content-box", n.cloneNode(!0).style.backgroundClip = "", ne.clearCloneStyle = "content-box" === n.style.backgroundClip, ne.boxSizing = "" === r.boxSizing || "" === r.MozBoxSizing || "" === r.WebkitBoxSizing, ie.extend(ne, {
                    reliableHiddenOffsets: function() {
                        return null == s && e(), s
                    },
                    boxSizingReliable: function() {
                        return null == a && e(), a
                    },
                    pixelPosition: function() {
                        return null == o && e(), o
                    },
                    reliableMarginRight: function() {
                        return null == u && e(), u
                    }
                }))
            }(), ie.swap = function(t, e, n, r) {
                var i, o, a = {};
                for (o in e) a[o] = t.style[o], t.style[o] = e[o];
                i = n.apply(t, r || []);
                for (o in e) t.style[o] = a[o];
                return i
            };
        var an = /alpha\([^)]*\)/i,
            sn = /opacity\s*=\s*([^)]*)/,
            un = /^(none|table(?!-c[ea]).+)/,
            ln = new RegExp("^(" + Se + ")(.*)$", "i"),
            cn = new RegExp("^([+-])=(" + Se + ")", "i"),
            fn = {
                position: "absolute",
                visibility: "hidden",
                display: "block"
            },
            dn = {
                letterSpacing: "0",
                fontWeight: "400"
            },
            pn = ["Webkit", "O", "Moz", "ms"];
        ie.extend({
            cssHooks: {
                opacity: {
                    get: function(t, e) {
                        if (e) {
                            var n = en(t, "opacity");
                            return "" === n ? "1" : n
                        }
                    }
                }
            },
            cssNumber: {
                columnCount: !0,
                fillOpacity: !0,
                flexGrow: !0,
                flexShrink: !0,
                fontWeight: !0,
                lineHeight: !0,
                opacity: !0,
                order: !0,
                orphans: !0,
                widows: !0,
                zIndex: !0,
                zoom: !0
            },
            cssProps: {
                "float": ne.cssFloat ? "cssFloat" : "styleFloat"
            },
            style: function(t, e, n, r) {
                if (t && 3 !== t.nodeType && 8 !== t.nodeType && t.style) {
                    var i, o, a, s = ie.camelCase(e),
                        u = t.style;
                    if (e = ie.cssProps[s] || (ie.cssProps[s] = j(u, s)), a = ie.cssHooks[e] || ie.cssHooks[s], void 0 === n) return a && "get" in a && void 0 !== (i = a.get(t, !1, r)) ? i : u[e];
                    if (o = typeof n, "string" === o && (i = cn.exec(n)) && (n = (i[1] + 1) * i[2] + parseFloat(ie.css(t, e)), o = "number"), null != n && n === n && ("number" !== o || ie.cssNumber[s] || (n += "px"), ne.clearCloneStyle || "" !== n || 0 !== e.indexOf("background") || (u[e] = "inherit"), !(a && "set" in a && void 0 === (n = a.set(t, n, r))))) try {
                        u[e] = n
                    } catch (l) {}
                }
            },
            css: function(t, e, n, r) {
                var i, o, a, s = ie.camelCase(e);
                return e = ie.cssProps[s] || (ie.cssProps[s] = j(t.style, s)), a = ie.cssHooks[e] || ie.cssHooks[s], a && "get" in a && (o = a.get(t, !0, n)), void 0 === o && (o = en(t, e, r)), "normal" === o && e in dn && (o = dn[e]), "" === n || n ? (i = parseFloat(o), n === !0 || ie.isNumeric(i) ? i || 0 : o) : o
            }
        }), ie.each(["height", "width"], function(t, e) {
            ie.cssHooks[e] = {
                get: function(t, n, r) {
                    return n ? un.test(ie.css(t, "display")) && 0 === t.offsetWidth ? ie.swap(t, fn, function() {
                        return $(t, e, r)
                    }) : $(t, e, r) : void 0
                },
                set: function(t, n, r) {
                    var i = r && tn(t);
                    return N(t, n, r ? A(t, e, r, ne.boxSizing && "border-box" === ie.css(t, "boxSizing", !1, i), i) : 0)
                }
            }
        }), ne.opacity || (ie.cssHooks.opacity = {
            get: function(t, e) {
                return sn.test((e && t.currentStyle ? t.currentStyle.filter : t.style.filter) || "") ? .01 * parseFloat(RegExp.$1) + "" : e ? "1" : ""
            },
            set: function(t, e) {
                var n = t.style,
                    r = t.currentStyle,
                    i = ie.isNumeric(e) ? "alpha(opacity=" + 100 * e + ")" : "",
                    o = r && r.filter || n.filter || "";
                n.zoom = 1, (e >= 1 || "" === e) && "" === ie.trim(o.replace(an, "")) && n.removeAttribute && (n.removeAttribute("filter"), "" === e || r && !r.filter) || (n.filter = an.test(o) ? o.replace(an, i) : o + " " + i)
            }
        }), ie.cssHooks.marginRight = S(ne.reliableMarginRight, function(t, e) {
            return e ? ie.swap(t, {
                display: "inline-block"
            }, en, [t, "marginRight"]) : void 0
        }), ie.each({
            margin: "",
            padding: "",
            border: "Width"
        }, function(t, e) {
            ie.cssHooks[t + e] = {
                expand: function(n) {
                    for (var r = 0, i = {}, o = "string" == typeof n ? n.split(" ") : [n]; 4 > r; r++) i[t + je[r] + e] = o[r] || o[r - 2] || o[0];
                    return i
                }
            }, nn.test(t) || (ie.cssHooks[t + e].set = N)
        }), ie.fn.extend({
            css: function(t, e) {
                return Ne(this, function(t, e, n) {
                    var r, i, o = {},
                        a = 0;
                    if (ie.isArray(e)) {
                        for (r = tn(t), i = e.length; i > a; a++) o[e[a]] = ie.css(t, e[a], !1, r);
                        return o
                    }
                    return void 0 !== n ? ie.style(t, e, n) : ie.css(t, e)
                }, t, e, arguments.length > 1)
            },
            show: function() {
                return E(this, !0)
            },
            hide: function() {
                return E(this)
            },
            toggle: function(t) {
                return "boolean" == typeof t ? t ? this.show() : this.hide() : this.each(function() {
                    Ee(this) ? ie(this).show() : ie(this).hide()
                })
            }
        }), ie.Tween = O, O.prototype = {
            constructor: O,
            init: function(t, e, n, r, i, o) {
                this.elem = t, this.prop = n, this.easing = i || "swing", this.options = e, this.start = this.now = this.cur(), this.end = r, this.unit = o || (ie.cssNumber[n] ? "" : "px")
            },
            cur: function() {
                var t = O.propHooks[this.prop];
                return t && t.get ? t.get(this) : O.propHooks._default.get(this)
            },
            run: function(t) {
                var e, n = O.propHooks[this.prop];
                return this.pos = e = this.options.duration ? ie.easing[this.easing](t, this.options.duration * t, 0, 1, this.options.duration) : t, this.now = (this.end - this.start) * e + this.start, this.options.step && this.options.step.call(this.elem, this.now, this), n && n.set ? n.set(this) : O.propHooks._default.set(this), this
            }
        }, O.prototype.init.prototype = O.prototype, O.propHooks = {
            _default: {
                get: function(t) {
                    var e;
                    return null == t.elem[t.prop] || t.elem.style && null != t.elem.style[t.prop] ? (e = ie.css(t.elem, t.prop, ""), e && "auto" !== e ? e : 0) : t.elem[t.prop]
                },
                set: function(t) {
                    ie.fx.step[t.prop] ? ie.fx.step[t.prop](t) : t.elem.style && (null != t.elem.style[ie.cssProps[t.prop]] || ie.cssHooks[t.prop]) ? ie.style(t.elem, t.prop, t.now + t.unit) : t.elem[t.prop] = t.now
                }
            }
        }, O.propHooks.scrollTop = O.propHooks.scrollLeft = {
            set: function(t) {
                t.elem.nodeType && t.elem.parentNode && (t.elem[t.prop] = t.now)
            }
        }, ie.easing = {
            linear: function(t) {
                return t
            },
            swing: function(t) {
                return .5 - Math.cos(t * Math.PI) / 2
            }
        }, ie.fx = O.prototype.init, ie.fx.step = {};
        var hn, gn, mn = /^(?:toggle|show|hide)$/,
            vn = new RegExp("^(?:([+-])=|)(" + Se + ")([a-z%]*)$", "i"),
            yn = /queueHooks$/,
            bn = [F],
            wn = {
                "*": [function(t, e) {
                    var n = this.createTween(t, e),
                        r = n.cur(),
                        i = vn.exec(e),
                        o = i && i[3] || (ie.cssNumber[t] ? "" : "px"),
                        a = (ie.cssNumber[t] || "px" !== o && +r) && vn.exec(ie.css(n.elem, t)),
                        s = 1,
                        u = 20;
                    if (a && a[3] !== o) {
                        o = o || a[3], i = i || [], a = +r || 1;
                        do s = s || ".5", a /= s, ie.style(n.elem, t, a + o); while (s !== (s = n.cur() / r) && 1 !== s && --u)
                    }
                    return i && (a = n.start = +a || +r || 0, n.unit = o, n.end = i[1] ? a + (i[1] + 1) * i[2] : +i[2]), n
                }]
            };
        ie.Animation = ie.extend(q, {
                tweener: function(t, e) {
                    ie.isFunction(t) ? (e = t, t = ["*"]) : t = t.split(" ");
                    for (var n, r = 0, i = t.length; i > r; r++) n = t[r], wn[n] = wn[n] || [], wn[n].unshift(e)
                },
                prefilter: function(t, e) {
                    e ? bn.unshift(t) : bn.push(t)
                }
            }), ie.speed = function(t, e, n) {
                var r = t && "object" == typeof t ? ie.extend({}, t) : {
                    complete: n || !n && e || ie.isFunction(t) && t,
                    duration: t,
                    easing: n && e || e && !ie.isFunction(e) && e
                };
                return r.duration = ie.fx.off ? 0 : "number" == typeof r.duration ? r.duration : r.duration in ie.fx.speeds ? ie.fx.speeds[r.duration] : ie.fx.speeds._default, (null == r.queue || r.queue === !0) && (r.queue = "fx"), r.old = r.complete, r.complete = function() {
                    ie.isFunction(r.old) && r.old.call(this), r.queue && ie.dequeue(this, r.queue)
                }, r
            }, ie.fn.extend({
                fadeTo: function(t, e, n, r) {
                    return this.filter(Ee).css("opacity", 0).show().end().animate({
                        opacity: e
                    }, t, n, r)
                },
                animate: function(t, e, n, r) {
                    var i = ie.isEmptyObject(t),
                        o = ie.speed(e, n, r),
                        a = function() {
                            var e = q(this, ie.extend({}, t), o);
                            (i || ie._data(this, "finish")) && e.stop(!0)
                        };
                    return a.finish = a, i || o.queue === !1 ? this.each(a) : this.queue(o.queue, a)
                },
                stop: function(t, e, n) {
                    var r = function(t) {
                        var e = t.stop;
                        delete t.stop, e(n)
                    };
                    return "string" != typeof t && (n = e, e = t, t = void 0), e && t !== !1 && this.queue(t || "fx", []), this.each(function() {
                        var e = !0,
                            i = null != t && t + "queueHooks",
                            o = ie.timers,
                            a = ie._data(this);
                        if (i) a[i] && a[i].stop && r(a[i]);
                        else
                            for (i in a) a[i] && a[i].stop && yn.test(i) && r(a[i]);
                        for (i = o.length; i--;) o[i].elem !== this || null != t && o[i].queue !== t || (o[i].anim.stop(n), e = !1, o.splice(i, 1));
                        (e || !n) && ie.dequeue(this, t)
                    })
                },
                finish: function(t) {
                    return t !== !1 && (t = t || "fx"), this.each(function() {
                        var e, n = ie._data(this),
                            r = n[t + "queue"],
                            i = n[t + "queueHooks"],
                            o = ie.timers,
                            a = r ? r.length : 0;
                        for (n.finish = !0, ie.queue(this, t, []), i && i.stop && i.stop.call(this, !0), e = o.length; e--;) o[e].elem === this && o[e].queue === t && (o[e].anim.stop(!0), o.splice(e, 1));
                        for (e = 0; a > e; e++) r[e] && r[e].finish && r[e].finish.call(this);
                        delete n.finish
                    })
                }
            }), ie.each(["toggle", "show", "hide"], function(t, e) {
                var n = ie.fn[e];
                ie.fn[e] = function(t, r, i) {
                    return null == t || "boolean" == typeof t ? n.apply(this, arguments) : this.animate(I(e, !0), t, r, i)
                }
            }), ie.each({
                slideDown: I("show"),
                slideUp: I("hide"),
                slideToggle: I("toggle"),
                fadeIn: {
                    opacity: "show"
                },
                fadeOut: {
                    opacity: "hide"
                },
                fadeToggle: {
                    opacity: "toggle"
                }
            }, function(t, e) {
                ie.fn[t] = function(t, n, r) {
                    return this.animate(e, t, n, r)
                }
            }), ie.timers = [], ie.fx.tick = function() {
                var t, e = ie.timers,
                    n = 0;
                for (hn = ie.now(); n < e.length; n++) t = e[n], t() || e[n] !== t || e.splice(n--, 1);
                e.length || ie.fx.stop(), hn = void 0
            }, ie.fx.timer = function(t) {
                ie.timers.push(t), t() ? ie.fx.start() : ie.timers.pop()
            }, ie.fx.interval = 13, ie.fx.start = function() {
                gn || (gn = setInterval(ie.fx.tick, ie.fx.interval))
            }, ie.fx.stop = function() {
                clearInterval(gn), gn = null
            }, ie.fx.speeds = {
                slow: 600,
                fast: 200,
                _default: 400
            }, ie.fn.delay = function(t, e) {
                return t = ie.fx ? ie.fx.speeds[t] || t : t, e = e || "fx", this.queue(e, function(e, n) {
                    var r = setTimeout(e, t);
                    n.stop = function() {
                        clearTimeout(r)
                    }
                })
            },
            function() {
                var t, e, n, r, i;
                e = he.createElement("div"), e.setAttribute("className", "t"), e.innerHTML = "  <link/><table></table><a href='/a'>a</a><input type='checkbox'/>", r = e.getElementsByTagName("a")[0], n = he.createElement("select"), i = n.appendChild(he.createElement("option")), t = e.getElementsByTagName("input")[0], r.style.cssText = "top:1px", ne.getSetAttribute = "t" !== e.className, ne.style = /top/.test(r.getAttribute("style")), ne.hrefNormalized = "/a" === r.getAttribute("href"), ne.checkOn = !!t.value, ne.optSelected = i.selected, ne.enctype = !!he.createElement("form").enctype, n.disabled = !0, ne.optDisabled = !i.disabled, t = he.createElement("input"), t.setAttribute("value", ""), ne.input = "" === t.getAttribute("value"), t.value = "t", t.setAttribute("type", "radio"), ne.radioValue = "t" === t.value
            }();
        var xn = /\r/g;
        ie.fn.extend({
            val: function(t) {
                var e, n, r, i = this[0]; {
                    if (arguments.length) return r = ie.isFunction(t), this.each(function(n) {
                        var i;
                        1 === this.nodeType && (i = r ? t.call(this, n, ie(this).val()) : t, null == i ? i = "" : "number" == typeof i ? i += "" : ie.isArray(i) && (i = ie.map(i, function(t) {
                            return null == t ? "" : t + ""
                        })), e = ie.valHooks[this.type] || ie.valHooks[this.nodeName.toLowerCase()], e && "set" in e && void 0 !== e.set(this, i, "value") || (this.value = i))
                    });
                    if (i) return e = ie.valHooks[i.type] || ie.valHooks[i.nodeName.toLowerCase()], e && "get" in e && void 0 !== (n = e.get(i, "value")) ? n : (n = i.value, "string" == typeof n ? n.replace(xn, "") : null == n ? "" : n)
                }
            }
        }), ie.extend({
            valHooks: {
                option: {
                    get: function(t) {
                        var e = ie.find.attr(t, "value");
                        return null != e ? e : ie.trim(ie.text(t))
                    }
                },
                select: {
                    get: function(t) {
                        for (var e, n, r = t.options, i = t.selectedIndex, o = "select-one" === t.type || 0 > i, a = o ? null : [], s = o ? i + 1 : r.length, u = 0 > i ? s : o ? i : 0; s > u; u++)
                            if (n = r[u], !(!n.selected && u !== i || (ne.optDisabled ? n.disabled : null !== n.getAttribute("disabled")) || n.parentNode.disabled && ie.nodeName(n.parentNode, "optgroup"))) {
                                if (e = ie(n).val(), o) return e;
                                a.push(e)
                            }
                        return a
                    },
                    set: function(t, e) {
                        for (var n, r, i = t.options, o = ie.makeArray(e), a = i.length; a--;)
                            if (r = i[a], ie.inArray(ie.valHooks.option.get(r), o) >= 0) try {
                                r.selected = n = !0
                            } catch (s) {
                                r.scrollHeight
                            } else r.selected = !1;
                        return n || (t.selectedIndex = -1), i
                    }
                }
            }
        }), ie.each(["radio", "checkbox"], function() {
            ie.valHooks[this] = {
                set: function(t, e) {
                    return ie.isArray(e) ? t.checked = ie.inArray(ie(t).val(), e) >= 0 : void 0
                }
            }, ne.checkOn || (ie.valHooks[this].get = function(t) {
                return null === t.getAttribute("value") ? "on" : t.value
            })
        });
        var _n, Cn, kn = ie.expr.attrHandle,
            Tn = /^(?:checked|selected)$/i,
            Sn = ne.getSetAttribute,
            jn = ne.input;
        ie.fn.extend({
            attr: function(t, e) {
                return Ne(this, ie.attr, t, e, arguments.length > 1)
            },
            removeAttr: function(t) {
                return this.each(function() {
                    ie.removeAttr(this, t)
                })
            }
        }), ie.extend({
            attr: function(t, e, n) {
                var r, i, o = t.nodeType;
                if (t && 3 !== o && 8 !== o && 2 !== o) return typeof t.getAttribute === Ce ? ie.prop(t, e, n) : (1 === o && ie.isXMLDoc(t) || (e = e.toLowerCase(), r = ie.attrHooks[e] || (ie.expr.match.bool.test(e) ? Cn : _n)), void 0 === n ? r && "get" in r && null !== (i = r.get(t, e)) ? i : (i = ie.find.attr(t, e), null == i ? void 0 : i) : null !== n ? r && "set" in r && void 0 !== (i = r.set(t, n, e)) ? i : (t.setAttribute(e, n + ""), n) : void ie.removeAttr(t, e))
            },
            removeAttr: function(t, e) {
                var n, r, i = 0,
                    o = e && e.match(be);
                if (o && 1 === t.nodeType)
                    for (; n = o[i++];) r = ie.propFix[n] || n, ie.expr.match.bool.test(n) ? jn && Sn || !Tn.test(n) ? t[r] = !1 : t[ie.camelCase("default-" + n)] = t[r] = !1 : ie.attr(t, n, ""), t.removeAttribute(Sn ? n : r)
            },
            attrHooks: {
                type: {
                    set: function(t, e) {
                        if (!ne.radioValue && "radio" === e && ie.nodeName(t, "input")) {
                            var n = t.value;
                            return t.setAttribute("type", e), n && (t.value = n), e
                        }
                    }
                }
            }
        }), Cn = {
            set: function(t, e, n) {
                return e === !1 ? ie.removeAttr(t, n) : jn && Sn || !Tn.test(n) ? t.setAttribute(!Sn && ie.propFix[n] || n, n) : t[ie.camelCase("default-" + n)] = t[n] = !0, n
            }
        }, ie.each(ie.expr.match.bool.source.match(/\w+/g), function(t, e) {
            var n = kn[e] || ie.find.attr;
            kn[e] = jn && Sn || !Tn.test(e) ? function(t, e, r) {
                var i, o;
                return r || (o = kn[e], kn[e] = i, i = null != n(t, e, r) ? e.toLowerCase() : null, kn[e] = o), i
            } : function(t, e, n) {
                return n ? void 0 : t[ie.camelCase("default-" + e)] ? e.toLowerCase() : null
            }
        }), jn && Sn || (ie.attrHooks.value = {
            set: function(t, e, n) {
                return ie.nodeName(t, "input") ? void(t.defaultValue = e) : _n && _n.set(t, e, n)
            }
        }), Sn || (_n = {
            set: function(t, e, n) {
                var r = t.getAttributeNode(n);
                return r || t.setAttributeNode(r = t.ownerDocument.createAttribute(n)), r.value = e += "", "value" === n || e === t.getAttribute(n) ? e : void 0
            }
        }, kn.id = kn.name = kn.coords = function(t, e, n) {
            var r;
            return n ? void 0 : (r = t.getAttributeNode(e)) && "" !== r.value ? r.value : null
        }, ie.valHooks.button = {
            get: function(t, e) {
                var n = t.getAttributeNode(e);
                return n && n.specified ? n.value : void 0
            },
            set: _n.set
        }, ie.attrHooks.contenteditable = {
            set: function(t, e, n) {
                _n.set(t, "" === e ? !1 : e, n)
            }
        }, ie.each(["width", "height"], function(t, e) {
            ie.attrHooks[e] = {
                set: function(t, n) {
                    return "" === n ? (t.setAttribute(e, "auto"), n) : void 0
                }
            }
        })), ne.style || (ie.attrHooks.style = {
            get: function(t) {
                return t.style.cssText || void 0
            },
            set: function(t, e) {
                return t.style.cssText = e + ""
            }
        });
        var En = /^(?:input|select|textarea|button|object)$/i,
            Nn = /^(?:a|area)$/i;
        ie.fn.extend({
            prop: function(t, e) {
                return Ne(this, ie.prop, t, e, arguments.length > 1)
            },
            removeProp: function(t) {
                return t = ie.propFix[t] || t, this.each(function() {
                    try {
                        this[t] = void 0, delete this[t]
                    } catch (e) {}
                })
            }
        }), ie.extend({
            propFix: {
                "for": "htmlFor",
                "class": "className"
            },
            prop: function(t, e, n) {
                var r, i, o, a = t.nodeType;
                if (t && 3 !== a && 8 !== a && 2 !== a) return o = 1 !== a || !ie.isXMLDoc(t), o && (e = ie.propFix[e] || e, i = ie.propHooks[e]), void 0 !== n ? i && "set" in i && void 0 !== (r = i.set(t, n, e)) ? r : t[e] = n : i && "get" in i && null !== (r = i.get(t, e)) ? r : t[e]
            },
            propHooks: {
                tabIndex: {
                    get: function(t) {
                        var e = ie.find.attr(t, "tabindex");
                        return e ? parseInt(e, 10) : En.test(t.nodeName) || Nn.test(t.nodeName) && t.href ? 0 : -1
                    }
                }
            }
        }), ne.hrefNormalized || ie.each(["href", "src"], function(t, e) {
            ie.propHooks[e] = {
                get: function(t) {
                    return t.getAttribute(e, 4)
                }
            }
        }), ne.optSelected || (ie.propHooks.selected = {
            get: function(t) {
                var e = t.parentNode;
                return e && (e.selectedIndex, e.parentNode && e.parentNode.selectedIndex), null
            }
        }), ie.each(["tabIndex", "readOnly", "maxLength", "cellSpacing", "cellPadding", "rowSpan", "colSpan", "useMap", "frameBorder", "contentEditable"], function() {
            ie.propFix[this.toLowerCase()] = this
        }), ne.enctype || (ie.propFix.enctype = "encoding");
        var An = /[\t\r\n\f]/g;
        ie.fn.extend({
            addClass: function(t) {
                var e, n, r, i, o, a, s = 0,
                    u = this.length,
                    l = "string" == typeof t && t;
                if (ie.isFunction(t)) return this.each(function(e) {
                    ie(this).addClass(t.call(this, e, this.className))
                });
                if (l)
                    for (e = (t || "").match(be) || []; u > s; s++)
                        if (n = this[s], r = 1 === n.nodeType && (n.className ? (" " + n.className + " ").replace(An, " ") : " ")) {
                            for (o = 0; i = e[o++];) r.indexOf(" " + i + " ") < 0 && (r += i + " ");
                            a = ie.trim(r), n.className !== a && (n.className = a)
                        }
                return this
            },
            removeClass: function(t) {
                var e, n, r, i, o, a, s = 0,
                    u = this.length,
                    l = 0 === arguments.length || "string" == typeof t && t;
                if (ie.isFunction(t)) return this.each(function(e) {
                    ie(this).removeClass(t.call(this, e, this.className))
                });
                if (l)
                    for (e = (t || "").match(be) || []; u > s; s++)
                        if (n = this[s], r = 1 === n.nodeType && (n.className ? (" " + n.className + " ").replace(An, " ") : "")) {
                            for (o = 0; i = e[o++];)
                                for (; r.indexOf(" " + i + " ") >= 0;) r = r.replace(" " + i + " ", " ");
                            a = t ? ie.trim(r) : "", n.className !== a && (n.className = a)
                        }
                return this
            },
            toggleClass: function(t, e) {
                var n = typeof t;
                return "boolean" == typeof e && "string" === n ? e ? this.addClass(t) : this.removeClass(t) : this.each(ie.isFunction(t) ? function(n) {
                    ie(this).toggleClass(t.call(this, n, this.className, e), e)
                } : function() {
                    if ("string" === n)
                        for (var e, r = 0, i = ie(this), o = t.match(be) || []; e = o[r++];) i.hasClass(e) ? i.removeClass(e) : i.addClass(e);
                    else(n === Ce || "boolean" === n) && (this.className && ie._data(this, "__className__", this.className), this.className = this.className || t === !1 ? "" : ie._data(this, "__className__") || "")
                })
            },
            hasClass: function(t) {
                for (var e = " " + t + " ", n = 0, r = this.length; r > n; n++)
                    if (1 === this[n].nodeType && (" " + this[n].className + " ").replace(An, " ").indexOf(e) >= 0) return !0;
                return !1
            }
        }), ie.each("blur focus focusin focusout load resize scroll unload click dblclick mousedown mouseup mousemove mouseover mouseout mouseenter mouseleave change select submit keydown keypress keyup error contextmenu".split(" "), function(t, e) {
            ie.fn[e] = function(t, n) {
                return arguments.length > 0 ? this.on(e, null, t, n) : this.trigger(e)
            }
        }), ie.fn.extend({
            hover: function(t, e) {
                return this.mouseenter(t).mouseleave(e || t)
            },
            bind: function(t, e, n) {
                return this.on(t, null, e, n)
            },
            unbind: function(t, e) {
                return this.off(t, null, e)
            },
            delegate: function(t, e, n, r) {
                return this.on(e, t, n, r)
            },
            undelegate: function(t, e, n) {
                return 1 === arguments.length ? this.off(t, "**") : this.off(e, t || "**", n)
            }
        });
        var $n = ie.now(),
            On = /\?/,
            Dn = /(,)|(\[|{)|(}|])|"(?:[^"\\\r\n]|\\["\\\/bfnrt]|\\u[\da-fA-F]{4})*"\s*:?|true|false|null|-?(?!0\d)\d+(?:\.\d+|)(?:[eE][+-]?\d+|)/g;
        ie.parseJSON = function(e) {
            if (t.JSON && t.JSON.parse) return t.JSON.parse(e + "");
            var n, r = null,
                i = ie.trim(e + "");
            return i && !ie.trim(i.replace(Dn, function(t, e, i, o) {
                return n && e && (r = 0), 0 === r ? t : (n = i || e, r += !o - !i, "")
            })) ? Function("return " + i)() : ie.error("Invalid JSON: " + e)
        }, ie.parseXML = function(e) {
            var n, r;
            if (!e || "string" != typeof e) return null;
            try {
                t.DOMParser ? (r = new DOMParser, n = r.parseFromString(e, "text/xml")) : (n = new ActiveXObject("Microsoft.XMLDOM"), n.async = "false", n.loadXML(e))
            } catch (i) {
                n = void 0
            }
            return n && n.documentElement && !n.getElementsByTagName("parsererror").length || ie.error("Invalid XML: " + e), n
        };
        var In, Ln, Fn = /#.*$/,
            Rn = /([?&])_=[^&]*/,
            qn = /^(.*?):[ \t]*([^\r\n]*)\r?$/gm,
            Mn = /^(?:about|app|app-storage|.+-extension|file|res|widget):$/,
            Pn = /^(?:GET|HEAD)$/,
            zn = /^\/\//,
            Hn = /^([\w.+-]+:)(?:\/\/(?:[^\/?#]*@|)([^\/?#:]*)(?::(\d+)|)|)/,
            Bn = {},
            Wn = {},
            Un = "*/".concat("*");
        try {
            Ln = location.href
        } catch (Vn) {
            Ln = he.createElement("a"), Ln.href = "", Ln = Ln.href
        }
        In = Hn.exec(Ln.toLowerCase()) || [], ie.extend({
            active: 0,
            lastModified: {},
            etag: {},
            ajaxSettings: {
                url: Ln,
                type: "GET",
                isLocal: Mn.test(In[1]),
                global: !0,
                processData: !0,
                async: !0,
                contentType: "application/x-www-form-urlencoded; charset=UTF-8",
                accepts: {
                    "*": Un,
                    text: "text/plain",
                    html: "text/html",
                    xml: "application/xml, text/xml",
                    json: "application/json, text/javascript"
                },
                contents: {
                    xml: /xml/,
                    html: /html/,
                    json: /json/
                },
                responseFields: {
                    xml: "responseXML",
                    text: "responseText",
                    json: "responseJSON"
                },
                converters: {
                    "* text": String,
                    "text html": !0,
                    "text json": ie.parseJSON,
                    "text xml": ie.parseXML
                },
                flatOptions: {
                    url: !0,
                    context: !0
                }
            },
            ajaxSetup: function(t, e) {
                return e ? z(z(t, ie.ajaxSettings), e) : z(ie.ajaxSettings, t)
            },
            ajaxPrefilter: M(Bn),
            ajaxTransport: M(Wn),
            ajax: function(t, e) {
                function n(t, e, n, r) {
                    var i, c, v, y, w, _ = e;
                    2 !== b && (b = 2, s && clearTimeout(s), l = void 0, a = r || "", x.readyState = t > 0 ? 4 : 0, i = t >= 200 && 300 > t || 304 === t, n && (y = H(f, x, n)), y = B(f, y, x, i), i ? (f.ifModified && (w = x.getResponseHeader("Last-Modified"), w && (ie.lastModified[o] = w), w = x.getResponseHeader("etag"), w && (ie.etag[o] = w)), 204 === t || "HEAD" === f.type ? _ = "nocontent" : 304 === t ? _ = "notmodified" : (_ = y.state, c = y.data, v = y.error, i = !v)) : (v = _, (t || !_) && (_ = "error", 0 > t && (t = 0))), x.status = t, x.statusText = (e || _) + "", i ? h.resolveWith(d, [c, _, x]) : h.rejectWith(d, [x, _, v]), x.statusCode(m), m = void 0, u && p.trigger(i ? "ajaxSuccess" : "ajaxError", [x, f, i ? c : v]), g.fireWith(d, [x, _]), u && (p.trigger("ajaxComplete", [x, f]), --ie.active || ie.event.trigger("ajaxStop")))
                }
                "object" == typeof t && (e = t, t = void 0), e = e || {};
                var r, i, o, a, s, u, l, c, f = ie.ajaxSetup({}, e),
                    d = f.context || f,
                    p = f.context && (d.nodeType || d.jquery) ? ie(d) : ie.event,
                    h = ie.Deferred(),
                    g = ie.Callbacks("once memory"),
                    m = f.statusCode || {},
                    v = {},
                    y = {},
                    b = 0,
                    w = "canceled",
                    x = {
                        readyState: 0,
                        getResponseHeader: function(t) {
                            var e;
                            if (2 === b) {
                                if (!c)
                                    for (c = {}; e = qn.exec(a);) c[e[1].toLowerCase()] = e[2];
                                e = c[t.toLowerCase()]
                            }
                            return null == e ? null : e
                        },
                        getAllResponseHeaders: function() {
                            return 2 === b ? a : null
                        },
                        setRequestHeader: function(t, e) {
                            var n = t.toLowerCase();
                            return b || (t = y[n] = y[n] || t, v[t] = e), this
                        },
                        overrideMimeType: function(t) {
                            return b || (f.mimeType = t), this
                        },
                        statusCode: function(t) {
                            var e;
                            if (t)
                                if (2 > b)
                                    for (e in t) m[e] = [m[e], t[e]];
                                else x.always(t[x.status]);
                            return this
                        },
                        abort: function(t) {
                            var e = t || w;
                            return l && l.abort(e), n(0, e), this
                        }
                    };
                if (h.promise(x).complete = g.add, x.success = x.done, x.error = x.fail, f.url = ((t || f.url || Ln) + "").replace(Fn, "").replace(zn, In[1] + "//"), f.type = e.method || e.type || f.method || f.type, f.dataTypes = ie.trim(f.dataType || "*").toLowerCase().match(be) || [""], null == f.crossDomain && (r = Hn.exec(f.url.toLowerCase()), f.crossDomain = !(!r || r[1] === In[1] && r[2] === In[2] && (r[3] || ("http:" === r[1] ? "80" : "443")) === (In[3] || ("http:" === In[1] ? "80" : "443")))), f.data && f.processData && "string" != typeof f.data && (f.data = ie.param(f.data, f.traditional)), P(Bn, f, e, x), 2 === b) return x;
                u = f.global, u && 0 === ie.active++ && ie.event.trigger("ajaxStart"), f.type = f.type.toUpperCase(), f.hasContent = !Pn.test(f.type), o = f.url, f.hasContent || (f.data && (o = f.url += (On.test(o) ? "&" : "?") + f.data, delete f.data), f.cache === !1 && (f.url = Rn.test(o) ? o.replace(Rn, "$1_=" + $n++) : o + (On.test(o) ? "&" : "?") + "_=" + $n++)), f.ifModified && (ie.lastModified[o] && x.setRequestHeader("If-Modified-Since", ie.lastModified[o]), ie.etag[o] && x.setRequestHeader("If-None-Match", ie.etag[o])), (f.data && f.hasContent && f.contentType !== !1 || e.contentType) && x.setRequestHeader("Content-Type", f.contentType), x.setRequestHeader("Accept", f.dataTypes[0] && f.accepts[f.dataTypes[0]] ? f.accepts[f.dataTypes[0]] + ("*" !== f.dataTypes[0] ? ", " + Un + "; q=0.01" : "") : f.accepts["*"]);
                for (i in f.headers) x.setRequestHeader(i, f.headers[i]);
                if (f.beforeSend && (f.beforeSend.call(d, x, f) === !1 || 2 === b)) return x.abort();
                w = "abort";
                for (i in {
                        success: 1,
                        error: 1,
                        complete: 1
                    }) x[i](f[i]);
                if (l = P(Wn, f, e, x)) {
                    x.readyState = 1, u && p.trigger("ajaxSend", [x, f]), f.async && f.timeout > 0 && (s = setTimeout(function() {
                        x.abort("timeout")
                    }, f.timeout));
                    try {
                        b = 1, l.send(v, n)
                    } catch (_) {
                        if (!(2 > b)) throw _;
                        n(-1, _)
                    }
                } else n(-1, "No Transport");
                return x
            },
            getJSON: function(t, e, n) {
                return ie.get(t, e, n, "json")
            },
            getScript: function(t, e) {
                return ie.get(t, void 0, e, "script")
            }
        }), ie.each(["get", "post"], function(t, e) {
            ie[e] = function(t, n, r, i) {
                return ie.isFunction(n) && (i = i || r, r = n, n = void 0), ie.ajax({
                    url: t,
                    type: e,
                    dataType: i,
                    data: n,
                    success: r
                })
            }
        }), ie.each(["ajaxStart", "ajaxStop", "ajaxComplete", "ajaxError", "ajaxSuccess", "ajaxSend"], function(t, e) {
            ie.fn[e] = function(t) {
                return this.on(e, t)
            }
        }), ie._evalUrl = function(t) {
            return ie.ajax({
                url: t,
                type: "GET",
                dataType: "script",
                async: !1,
                global: !1,
                "throws": !0
            })
        }, ie.fn.extend({
            wrapAll: function(t) {
                if (ie.isFunction(t)) return this.each(function(e) {
                    ie(this).wrapAll(t.call(this, e))
                });
                if (this[0]) {
                    var e = ie(t, this[0].ownerDocument).eq(0).clone(!0);
                    this[0].parentNode && e.insertBefore(this[0]), e.map(function() {
                        for (var t = this; t.firstChild && 1 === t.firstChild.nodeType;) t = t.firstChild;
                        return t
                    }).append(this)
                }
                return this
            },
            wrapInner: function(t) {
                return this.each(ie.isFunction(t) ? function(e) {
                    ie(this).wrapInner(t.call(this, e))
                } : function() {
                    var e = ie(this),
                        n = e.contents();
                    n.length ? n.wrapAll(t) : e.append(t)
                })
            },
            wrap: function(t) {
                var e = ie.isFunction(t);
                return this.each(function(n) {
                    ie(this).wrapAll(e ? t.call(this, n) : t)
                })
            },
            unwrap: function() {
                return this.parent().each(function() {
                    ie.nodeName(this, "body") || ie(this).replaceWith(this.childNodes)
                }).end()
            }
        }), ie.expr.filters.hidden = function(t) {
            return t.offsetWidth <= 0 && t.offsetHeight <= 0 || !ne.reliableHiddenOffsets() && "none" === (t.style && t.style.display || ie.css(t, "display"))
        }, ie.expr.filters.visible = function(t) {
            return !ie.expr.filters.hidden(t)
        };
        var Kn = /%20/g,
            Xn = /\[\]$/,
            Qn = /\r?\n/g,
            Gn = /^(?:submit|button|image|reset|file)$/i,
            Jn = /^(?:input|select|textarea|keygen)/i;
        ie.param = function(t, e) {
            var n, r = [],
                i = function(t, e) {
                    e = ie.isFunction(e) ? e() : null == e ? "" : e, r[r.length] = encodeURIComponent(t) + "=" + encodeURIComponent(e)
                };
            if (void 0 === e && (e = ie.ajaxSettings && ie.ajaxSettings.traditional), ie.isArray(t) || t.jquery && !ie.isPlainObject(t)) ie.each(t, function() {
                i(this.name, this.value)
            });
            else
                for (n in t) W(n, t[n], e, i);
            return r.join("&").replace(Kn, "+")
        }, ie.fn.extend({
            serialize: function() {
                return ie.param(this.serializeArray())
            },
            serializeArray: function() {
                return this.map(function() {
                    var t = ie.prop(this, "elements");
                    return t ? ie.makeArray(t) : this
                }).filter(function() {
                    var t = this.type;
                    return this.name && !ie(this).is(":disabled") && Jn.test(this.nodeName) && !Gn.test(t) && (this.checked || !Ae.test(t))
                }).map(function(t, e) {
                    var n = ie(this).val();
                    return null == n ? null : ie.isArray(n) ? ie.map(n, function(t) {
                        return {
                            name: e.name,
                            value: t.replace(Qn, "\r\n")
                        }
                    }) : {
                        name: e.name,
                        value: n.replace(Qn, "\r\n")
                    }
                }).get()
            }
        }), ie.ajaxSettings.xhr = void 0 !== t.ActiveXObject ? function() {
            return !this.isLocal && /^(get|post|head|put|delete|options)$/i.test(this.type) && U() || V()
        } : U;
        var Zn = 0,
            Yn = {},
            tr = ie.ajaxSettings.xhr();
        t.ActiveXObject && ie(t).on("unload", function() {
            for (var t in Yn) Yn[t](void 0, !0)
        }), ne.cors = !!tr && "withCredentials" in tr, tr = ne.ajax = !!tr, tr && ie.ajaxTransport(function(t) {
            if (!t.crossDomain || ne.cors) {
                var e;
                return {
                    send: function(n, r) {
                        var i, o = t.xhr(),
                            a = ++Zn;
                        if (o.open(t.type, t.url, t.async, t.username, t.password), t.xhrFields)
                            for (i in t.xhrFields) o[i] = t.xhrFields[i];
                        t.mimeType && o.overrideMimeType && o.overrideMimeType(t.mimeType), t.crossDomain || n["X-Requested-With"] || (n["X-Requested-With"] = "XMLHttpRequest");
                        for (i in n) void 0 !== n[i] && o.setRequestHeader(i, n[i] + "");
                        o.send(t.hasContent && t.data || null), e = function(n, i) {
                            var s, u, l;
                            if (e && (i || 4 === o.readyState))
                                if (delete Yn[a], e = void 0, o.onreadystatechange = ie.noop, i) 4 !== o.readyState && o.abort();
                                else {
                                    l = {}, s = o.status, "string" == typeof o.responseText && (l.text = o.responseText);
                                    try {
                                        u = o.statusText
                                    } catch (c) {
                                        u = ""
                                    }
                                    s || !t.isLocal || t.crossDomain ? 1223 === s && (s = 204) : s = l.text ? 200 : 404
                                }
                            l && r(s, u, l, o.getAllResponseHeaders())
                        }, t.async ? 4 === o.readyState ? setTimeout(e) : o.onreadystatechange = Yn[a] = e : e()
                    },
                    abort: function() {
                        e && e(void 0, !0)
                    }
                }
            }
        }), ie.ajaxSetup({
            accepts: {
                script: "text/javascript, application/javascript, application/ecmascript, application/x-ecmascript"
            },
            contents: {
                script: /(?:java|ecma)script/
            },
            converters: {
                "text script": function(t) {
                    return ie.globalEval(t), t
                }
            }
        }), ie.ajaxPrefilter("script", function(t) {
            void 0 === t.cache && (t.cache = !1), t.crossDomain && (t.type = "GET", t.global = !1)
        }), ie.ajaxTransport("script", function(t) {
            if (t.crossDomain) {
                var e, n = he.head || ie("head")[0] || he.documentElement;
                return {
                    send: function(r, i) {
                        e = he.createElement("script"), e.async = !0, t.scriptCharset && (e.charset = t.scriptCharset), e.src = t.url, e.onload = e.onreadystatechange = function(t, n) {
                            (n || !e.readyState || /loaded|complete/.test(e.readyState)) && (e.onload = e.onreadystatechange = null, e.parentNode && e.parentNode.removeChild(e), e = null, n || i(200, "success"))
                        }, n.insertBefore(e, n.firstChild)
                    },
                    abort: function() {
                        e && e.onload(void 0, !0)
                    }
                }
            }
        });
        var er = [],
            nr = /(=)\?(?=&|$)|\?\?/;
        ie.ajaxSetup({
            jsonp: "callback",
            jsonpCallback: function() {
                var t = er.pop() || ie.expando + "_" + $n++;
                return this[t] = !0, t
            }
        }), ie.ajaxPrefilter("json jsonp", function(e, n, r) {
            var i, o, a, s = e.jsonp !== !1 && (nr.test(e.url) ? "url" : "string" == typeof e.data && !(e.contentType || "").indexOf("application/x-www-form-urlencoded") && nr.test(e.data) && "data");
            return s || "jsonp" === e.dataTypes[0] ? (i = e.jsonpCallback = ie.isFunction(e.jsonpCallback) ? e.jsonpCallback() : e.jsonpCallback, s ? e[s] = e[s].replace(nr, "$1" + i) : e.jsonp !== !1 && (e.url += (On.test(e.url) ? "&" : "?") + e.jsonp + "=" + i), e.converters["script json"] = function() {
                return a || ie.error(i + " was not called"), a[0]
            }, e.dataTypes[0] = "json", o = t[i], t[i] = function() {
                a = arguments
            }, r.always(function() {
                t[i] = o, e[i] && (e.jsonpCallback = n.jsonpCallback, er.push(i)), a && ie.isFunction(o) && o(a[0]), a = o = void 0
            }), "script") : void 0
        }), ie.parseHTML = function(t, e, n) {
            if (!t || "string" != typeof t) return null;
            "boolean" == typeof e && (n = e, e = !1), e = e || he;
            var r = fe.exec(t),
                i = !n && [];
            return r ? [e.createElement(r[1])] : (r = ie.buildFragment([t], e, i), i && i.length && ie(i).remove(), ie.merge([], r.childNodes))
        };
        var rr = ie.fn.load;
        ie.fn.load = function(t, e, n) {
            if ("string" != typeof t && rr) return rr.apply(this, arguments);
            var r, i, o, a = this,
                s = t.indexOf(" ");
            return s >= 0 && (r = ie.trim(t.slice(s, t.length)), t = t.slice(0, s)), ie.isFunction(e) ? (n = e, e = void 0) : e && "object" == typeof e && (o = "POST"), a.length > 0 && ie.ajax({
                url: t,
                type: o,
                dataType: "html",
                data: e
            }).done(function(t) {
                i = arguments, a.html(r ? ie("<div>").append(ie.parseHTML(t)).find(r) : t)
            }).complete(n && function(t, e) {
                a.each(n, i || [t.responseText, e, t])
            }), this
        }, ie.expr.filters.animated = function(t) {
            return ie.grep(ie.timers, function(e) {
                return t === e.elem
            }).length
        };
        var ir = t.document.documentElement;
        ie.offset = {
            setOffset: function(t, e, n) {
                var r, i, o, a, s, u, l, c = ie.css(t, "position"),
                    f = ie(t),
                    d = {};
                "static" === c && (t.style.position = "relative"), s = f.offset(), o = ie.css(t, "top"), u = ie.css(t, "left"), l = ("absolute" === c || "fixed" === c) && ie.inArray("auto", [o, u]) > -1, l ? (r = f.position(), a = r.top, i = r.left) : (a = parseFloat(o) || 0, i = parseFloat(u) || 0), ie.isFunction(e) && (e = e.call(t, n, s)), null != e.top && (d.top = e.top - s.top + a), null != e.left && (d.left = e.left - s.left + i), "using" in e ? e.using.call(t, d) : f.css(d)
            }
        }, ie.fn.extend({
            offset: function(t) {
                if (arguments.length) return void 0 === t ? this : this.each(function(e) {
                    ie.offset.setOffset(this, t, e)
                });
                var e, n, r = {
                        top: 0,
                        left: 0
                    },
                    i = this[0],
                    o = i && i.ownerDocument;
                if (o) return e = o.documentElement, ie.contains(e, i) ? (typeof i.getBoundingClientRect !== Ce && (r = i.getBoundingClientRect()), n = K(o), {
                    top: r.top + (n.pageYOffset || e.scrollTop) - (e.clientTop || 0),
                    left: r.left + (n.pageXOffset || e.scrollLeft) - (e.clientLeft || 0)
                }) : r
            },
            position: function() {
                if (this[0]) {
                    var t, e, n = {
                            top: 0,
                            left: 0
                        },
                        r = this[0];
                    return "fixed" === ie.css(r, "position") ? e = r.getBoundingClientRect() : (t = this.offsetParent(), e = this.offset(), ie.nodeName(t[0], "html") || (n = t.offset()), n.top += ie.css(t[0], "borderTopWidth", !0), n.left += ie.css(t[0], "borderLeftWidth", !0)), {
                        top: e.top - n.top - ie.css(r, "marginTop", !0),
                        left: e.left - n.left - ie.css(r, "marginLeft", !0)
                    }
                }
            },
            offsetParent: function() {
                return this.map(function() {
                    for (var t = this.offsetParent || ir; t && !ie.nodeName(t, "html") && "static" === ie.css(t, "position");) t = t.offsetParent;
                    return t || ir
                })
            }
        }), ie.each({
            scrollLeft: "pageXOffset",
            scrollTop: "pageYOffset"
        }, function(t, e) {
            var n = /Y/.test(e);
            ie.fn[t] = function(r) {
                return Ne(this, function(t, r, i) {
                    var o = K(t);
                    return void 0 === i ? o ? e in o ? o[e] : o.document.documentElement[r] : t[r] : void(o ? o.scrollTo(n ? ie(o).scrollLeft() : i, n ? i : ie(o).scrollTop()) : t[r] = i)
                }, t, r, arguments.length, null)
            }
        }), ie.each(["top", "left"], function(t, e) {
            ie.cssHooks[e] = S(ne.pixelPosition, function(t, n) {
                return n ? (n = en(t, e), rn.test(n) ? ie(t).position()[e] + "px" : n) : void 0
            })
        }), ie.each({
            Height: "height",
            Width: "width"
        }, function(t, e) {
            ie.each({
                padding: "inner" + t,
                content: e,
                "": "outer" + t
            }, function(n, r) {
                ie.fn[r] = function(r, i) {
                    var o = arguments.length && (n || "boolean" != typeof r),
                        a = n || (r === !0 || i === !0 ? "margin" : "border");
                    return Ne(this, function(e, n, r) {
                        var i;
                        return ie.isWindow(e) ? e.document.documentElement["client" + t] : 9 === e.nodeType ? (i = e.documentElement, Math.max(e.body["scroll" + t], i["scroll" + t], e.body["offset" + t], i["offset" + t], i["client" + t])) : void 0 === r ? ie.css(e, n, a) : ie.style(e, n, r, a)
                    }, e, o ? r : void 0, o, null)
                }
            })
        }), ie.fn.size = function() {
            return this.length
        }, ie.fn.andSelf = ie.fn.addBack, "function" == typeof define && define.amd && define("jquery", [], function() {
            return ie
        });
        var or = t.jQuery,
            ar = t.$;
        return ie.noConflict = function(e) {
            return t.$ === ie && (t.$ = ar), e && t.jQuery === ie && (t.jQuery = or), ie
        }, typeof e === Ce && (t.jQuery = t.$ = ie), ie
    }), function(t, e) {
        t.rails !== e && t.error("jquery-ujs has already been loaded!");
        var n, r = t(document);
        t.rails = n = {
            linkClickSelector: "a[data-confirm], a[data-method], a[data-remote], a[data-disable-with], a[data-disable]",
            buttonClickSelector: "button[data-remote]:not(form button), button[data-confirm]:not(form button)",
            inputChangeSelector: "select[data-remote], input[data-remote], textarea[data-remote]",
            formSubmitSelector: "form",
            formInputClickSelector: "form input[type=submit], form input[type=image], form button[type=submit], form button:not([type]), input[type=submit][form], input[type=image][form], button[type=submit][form], button[form]:not([type])",
            disableSelector: "input[data-disable-with]:enabled, button[data-disable-with]:enabled, textarea[data-disable-with]:enabled, input[data-disable]:enabled, button[data-disable]:enabled, textarea[data-disable]:enabled",
            enableSelector: "input[data-disable-with]:disabled, button[data-disable-with]:disabled, textarea[data-disable-with]:disabled, input[data-disable]:disabled, button[data-disable]:disabled, textarea[data-disable]:disabled",
            requiredInputSelector: "input[name][required]:not([disabled]),textarea[name][required]:not([disabled])",
            fileInputSelector: "input[type=file]",
            linkDisableSelector: "a[data-disable-with], a[data-disable]",
            buttonDisableSelector: "button[data-remote][data-disable-with], button[data-remote][data-disable]",
            CSRFProtection: function(e) {
                var n = t('meta[name="csrf-token"]').attr("content");
                n && e.setRequestHeader("X-CSRF-Token", n)
            },
            refreshCSRFTokens: function() {
                var e = t("meta[name=csrf-token]").attr("content"),
                    n = t("meta[name=csrf-param]").attr("content");
                t('form input[name="' + n + '"]').val(e)
            },
            fire: function(e, n, r) {
                var i = t.Event(n);
                return e.trigger(i, r), i.result !== !1
            },
            confirm: function(t) {
                return confirm(t)
            },
            ajax: function(e) {
                return t.ajax(e)
            },
            href: function(t) {
                return t[0].href
            },
            handleRemote: function(r) {
                var i, o, a, s, u, l;
                if (n.fire(r, "ajax:before")) {
                    if (s = r.data("with-credentials") || null, u = r.data("type") || t.ajaxSettings && t.ajaxSettings.dataType, r.is("form")) {
                        i = r.attr("method"), o = r.attr("action"), a = r.serializeArray();
                        var c = r.data("ujs:submit-button");
                        c && (a.push(c), r.data("ujs:submit-button", null))
                    } else r.is(n.inputChangeSelector) ? (i = r.data("method"), o = r.data("url"), a = r.serialize(), r.data("params") && (a = a + "&" + r.data("params"))) : r.is(n.buttonClickSelector) ? (i = r.data("method") || "get", o = r.data("url"), a = r.serialize(), r.data("params") && (a = a + "&" + r.data("params"))) : (i = r.data("method"), o = n.href(r), a = r.data("params") || null);
                    return l = {
                        type: i || "GET",
                        data: a,
                        dataType: u,
                        beforeSend: function(t, i) {
                            return i.dataType === e && t.setRequestHeader("accept", "*/*;q=0.5, " + i.accepts.script), n.fire(r, "ajax:beforeSend", [t, i]) ? void r.trigger("ajax:send", t) : !1
                        },
                        success: function(t, e, n) {
                            r.trigger("ajax:success", [t, e, n])
                        },
                        complete: function(t, e) {
                            r.trigger("ajax:complete", [t, e])
                        },
                        error: function(t, e, n) {
                            r.trigger("ajax:error", [t, e, n])
                        },
                        crossDomain: n.isCrossDomain(o)
                    }, s && (l.xhrFields = {
                        withCredentials: s
                    }), o && (l.url = o), n.ajax(l)
                }
                return !1
            },
            isCrossDomain: function(t) {
                var e = document.createElement("a");
                e.href = location.href;
                var n = document.createElement("a");
                try {
                    return n.href = t, n.href = n.href, !n.protocol || !n.host || e.protocol + "//" + e.host != n.protocol + "//" + n.host
                } catch (r) {
                    return !0
                }
            },
            handleMethod: function(r) {
                var i = n.href(r),
                    o = r.data("method"),
                    a = r.attr("target"),
                    s = t("meta[name=csrf-token]").attr("content"),
                    u = t("meta[name=csrf-param]").attr("content"),
                    l = t('<form method="post" action="' + i + '"></form>'),
                    c = '<input name="_method" value="' + o + '" type="hidden" />';
                u === e || s === e || n.isCrossDomain(i) || (c += '<input name="' + u + '" value="' + s + '" type="hidden" />'), a && l.attr("target", a), l.hide().append(c).appendTo("body"), l.submit()
            },
            formElements: function(e, n) {
                return e.is("form") ? t(e[0].elements).filter(n) : e.find(n)
            },
            disableFormElements: function(e) {
                n.formElements(e, n.disableSelector).each(function() {
                    n.disableFormElement(t(this))
                })
            },
            disableFormElement: function(t) {
                var n, r;
                n = t.is("button") ? "html" : "val", r = t.data("disable-with"), t.data("ujs:enable-with", t[n]()), r !== e && t[n](r), t.prop("disabled", !0)
            },
            enableFormElements: function(e) {
                n.formElements(e, n.enableSelector).each(function() {
                    n.enableFormElement(t(this))
                })
            },
            enableFormElement: function(t) {
                var e = t.is("button") ? "html" : "val";
                t.data("ujs:enable-with") && t[e](t.data("ujs:enable-with")), t.prop("disabled", !1)
            },
            allowAction: function(t) {
                var e, r = t.data("confirm"),
                    i = !1;
                return r ? (n.fire(t, "confirm") && (i = n.confirm(r), e = n.fire(t, "confirm:complete", [i])), i && e) : !0
            },
            blankInputs: function(e, n, r) {
                var i, o, a = t(),
                    s = n || "input,textarea",
                    u = e.find(s);
                return u.each(function() {
                    if (i = t(this), o = i.is("input[type=checkbox],input[type=radio]") ? i.is(":checked") : i.val(), !o == !r) {
                        if (i.is("input[type=radio]") && u.filter('input[type=radio]:checked[name="' + i.attr("name") + '"]').length) return !0;
                        a = a.add(i)
                    }
                }), a.length ? a : !1
            },
            nonBlankInputs: function(t, e) {
                return n.blankInputs(t, e, !0)
            },
            stopEverything: function(e) {
                return t(e.target).trigger("ujs:everythingStopped"), e.stopImmediatePropagation(), !1
            },
            disableElement: function(t) {
                var r = t.data("disable-with");
                t.data("ujs:enable-with", t.html()), r !== e && t.html(r), t.bind("click.railsDisable", function(t) {
                    return n.stopEverything(t)
                })
            },
            enableElement: function(t) {
                t.data("ujs:enable-with") !== e && (t.html(t.data("ujs:enable-with")), t.removeData("ujs:enable-with")), t.unbind("click.railsDisable")
            }
        }, n.fire(r, "rails:attachBindings") && (t.ajaxPrefilter(function(t, e, r) {
            t.crossDomain || n.CSRFProtection(r)
        }), r.delegate(n.linkDisableSelector, "ajax:complete", function() {
            n.enableElement(t(this))
        }), r.delegate(n.buttonDisableSelector, "ajax:complete", function() {
            n.enableFormElement(t(this))
        }), r.delegate(n.linkClickSelector, "click.rails", function(r) {
            var i = t(this),
                o = i.data("method"),
                a = i.data("params"),
                s = r.metaKey || r.ctrlKey;
            if (!n.allowAction(i)) return n.stopEverything(r);
            if (!s && i.is(n.linkDisableSelector) && n.disableElement(i), i.data("remote") !== e) {
                if (s && (!o || "GET" === o) && !a) return !0;
                var u = n.handleRemote(i);
                return u === !1 ? n.enableElement(i) : u.error(function() {
                    n.enableElement(i)
                }), !1
            }
            return i.data("method") ? (n.handleMethod(i), !1) : void 0
        }), r.delegate(n.buttonClickSelector, "click.rails", function(e) {
            var r = t(this);
            if (!n.allowAction(r)) return n.stopEverything(e);
            r.is(n.buttonDisableSelector) && n.disableFormElement(r);
            var i = n.handleRemote(r);
            return i === !1 ? n.enableFormElement(r) : i.error(function() {
                n.enableFormElement(r)
            }), !1
        }), r.delegate(n.inputChangeSelector, "change.rails", function(e) {
            var r = t(this);
            return n.allowAction(r) ? (n.handleRemote(r), !1) : n.stopEverything(e)
        }), r.delegate(n.formSubmitSelector, "submit.rails", function(r) {
            var i, o, a = t(this),
                s = a.data("remote") !== e;
            if (!n.allowAction(a)) return n.stopEverything(r);
            if (a.attr("novalidate") == e && (i = n.blankInputs(a, n.requiredInputSelector), i && n.fire(a, "ajax:aborted:required", [i]))) return n.stopEverything(r);
            if (s) {
                if (o = n.nonBlankInputs(a, n.fileInputSelector)) {
                    setTimeout(function() {
                        n.disableFormElements(a)
                    }, 13);
                    var u = n.fire(a, "ajax:aborted:file", [o]);
                    return u || setTimeout(function() {
                        n.enableFormElements(a)
                    }, 13), u
                }
                return n.handleRemote(a), !1
            }
            setTimeout(function() {
                n.disableFormElements(a)
            }, 13)
        }), r.delegate(n.formInputClickSelector, "click.rails", function(e) {
            var r = t(this);
            if (!n.allowAction(r)) return n.stopEverything(e);
            var i = r.attr("name"),
                o = i ? {
                    name: i,
                    value: r.val()
                } : null;
            r.closest("form").data("ujs:submit-button", o)
        }), r.delegate(n.formSubmitSelector, "ajax:send.rails", function(e) {
            this == e.target && n.disableFormElements(t(this))
        }), r.delegate(n.formSubmitSelector, "ajax:complete.rails", function(e) {
            this == e.target && n.enableFormElements(t(this))
        }), t(function() {
            n.refreshCSRFTokens()
        }))
    }(jQuery), function(t) {
        "function" == typeof define && define.amd ? define(["jquery"], function(e) {
            return t(e)
        }) : "object" == typeof module && "object" == typeof module.exports ? module.exports = t(require("jquery")) : t(window.jQuery)
    }(function(t) {
        "use strict";

        function e(t) {
            void 0 === t && (t = window.navigator.userAgent), t = t.toLowerCase();
            var e = /(edge)\/([\w.]+)/.exec(t) || /(opr)[\/]([\w.]+)/.exec(t) || /(chrome)[ \/]([\w.]+)/.exec(t) || /(version)(applewebkit)[ \/]([\w.]+).*(safari)[ \/]([\w.]+)/.exec(t) || /(webkit)[ \/]([\w.]+).*(version)[ \/]([\w.]+).*(safari)[ \/]([\w.]+)/.exec(t) || /(webkit)[ \/]([\w.]+)/.exec(t) || /(opera)(?:.*version|)[ \/]([\w.]+)/.exec(t) || /(msie) ([\w.]+)/.exec(t) || t.indexOf("trident") >= 0 && /(rv)(?::| )([\w.]+)/.exec(t) || t.indexOf("compatible") < 0 && /(mozilla)(?:.*? rv:([\w.]+)|)/.exec(t) || [],
                n = /(ipad)/.exec(t) || /(ipod)/.exec(t) || /(iphone)/.exec(t) || /(kindle)/.exec(t) || /(silk)/.exec(t) || /(android)/.exec(t) || /(windows phone)/.exec(t) || /(win)/.exec(t) || /(mac)/.exec(t) || /(linux)/.exec(t) || /(cros)/.exec(t) || /(playbook)/.exec(t) || /(bb)/.exec(t) || /(blackberry)/.exec(t) || [],
                r = {},
                i = {
                    browser: e[5] || e[3] || e[1] || "",
                    version: e[2] || e[4] || "0",
                    versionNumber: e[4] || e[2] || "0",
                    platform: n[0] || ""
                };
            if (i.browser && (r[i.browser] = !0, r.version = i.version, r.versionNumber = parseInt(i.versionNumber, 10)), i.platform && (r[i.platform] = !0), (r.android || r.bb || r.blackberry || r.ipad || r.iphone || r.ipod || r.kindle || r.playbook || r.silk || r["windows phone"]) && (r.mobile = !0), (r.cros || r.mac || r.linux || r.win) && (r.desktop = !0), (r.chrome || r.opr || r.safari) && (r.webkit = !0), r.rv || r.edge) {
                var o = "msie";
                i.browser = o, r[o] = !0
            }
            if (r.safari && r.blackberry) {
                var a = "blackberry";
                i.browser = a, r[a] = !0
            }
            if (r.safari && r.playbook) {
                var s = "playbook";
                i.browser = s, r[s] = !0
            }
            if (r.bb) {
                var u = "blackberry";
                i.browser = u, r[u] = !0
            }
            if (r.opr) {
                var l = "opera";
                i.browser = l, r[l] = !0
            }
            if (r.safari && r.android) {
                var c = "android";
                i.browser = c, r[c] = !0
            }
            if (r.safari && r.kindle) {
                var f = "kindle";
                i.browser = f, r[f] = !0
            }
            if (r.safari && r.silk) {
                var d = "silk";
                i.browser = d, r[d] = !0
            }
            return r.name = i.browser, r.platform = i.platform, r
        }
        return window.jQBrowser = e(window.navigator.userAgent), window.jQBrowser.uaMatch = e, t && (t.browser = window.jQBrowser), window.jQBrowser
    }), function(t) {
        function e(e, r, i) {
            var o = this;
            return this.on("click.pjax", e, function(e) {
                var a = t.extend({}, d(r, i));
                a.container || (a.container = t(this).attr("data-pjax") || o), n(e, a)
            })
        }

        function n(e, n, r) {
            r = d(n, r);
            var o = e.currentTarget;
            if ("A" !== o.tagName.toUpperCase()) throw "$.fn.pjax or $.pjax.click requires an anchor element";
            if (!(e.which > 1 || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey || location.protocol !== o.protocol || location.hostname !== o.hostname || o.hash && o.href.replace(o.hash, "") === location.href.replace(location.hash, "") || o.href === location.href + "#" || e.isDefaultPrevented())) {
                var a = {
                        url: o.href,
                        container: t(o).attr("data-pjax"),
                        target: o
                    },
                    s = t.extend({}, a, r),
                    u = t.Event("pjax:click");
                t(o).trigger(u, [s]), u.isDefaultPrevented() || (i(s), e.preventDefault(), t(o).trigger("pjax:clicked", [s]))
            }
        }

        function r(e, n, r) {
            r = d(n, r);
            var o = e.currentTarget;
            if ("FORM" !== o.tagName.toUpperCase()) throw "$.pjax.submit requires a form element";
            var a = {
                type: o.method.toUpperCase(),
                url: o.action,
                data: t(o).serializeArray(),
                container: t(o).attr("data-pjax"),
                target: o
            };
            i(t.extend({}, a, r)), e.preventDefault()
        }

        function i(e) {
            function n(e, n, i) {
                i || (i = {}), i.relatedTarget = r;
                var o = t.Event(e, i);
                return s.trigger(o, n), !o.isDefaultPrevented()
            }
            e = t.extend(!0, {}, t.ajaxSettings, i.defaults, e), t.isFunction(e.url) && (e.url = e.url());
            var r = e.target,
                o = f(e.url).hash,
                s = e.context = p(e.container);
            e.data || (e.data = {}), e.data._pjax = s.selector;
            var u;
            e.beforeSend = function(t, r) {
                return "GET" !== r.type && (r.timeout = 0), t.setRequestHeader("X-PJAX", "true"), t.setRequestHeader("X-PJAX-Container", s.selector), n("pjax:beforeSend", [t, r]) ? (r.timeout > 0 && (u = setTimeout(function() {
                    n("pjax:timeout", [t, e]) && t.abort("timeout")
                }, r.timeout), r.timeout = 0), void(e.requestUrl = f(r.url).href)) : !1
            }, e.complete = function(t, r) {
                u && clearTimeout(u), n("pjax:complete", [t, r, e]), n("pjax:end", [t, e])
            }, e.error = function(t, r, i) {
                var o = m("", t, e),
                    s = n("pjax:error", [t, r, i, e]);
                "GET" == e.type && "abort" !== r && s && a(o.url)
            }, e.success = function(r, u, c) {
                var d = i.state,
                    p = "function" == typeof t.pjax.defaults.version ? t.pjax.defaults.version() : t.pjax.defaults.version,
                    h = c.getResponseHeader("X-PJAX-Version"),
                    g = m(r, c, e);
                if (p && h && p !== h) return void a(g.url);
                if (!g.contents) return void a(g.url);
                i.state = {
                    id: e.id || l(),
                    url: g.url,
                    title: g.title,
                    container: s.selector,
                    fragment: e.fragment,
                    timeout: e.timeout
                }, (e.push || e.replace) && window.history.replaceState(i.state, g.title, g.url);
                try {
                    document.activeElement.blur()
                } catch (y) {}
                g.title && (document.title = g.title), n("pjax:beforeReplace", [g.contents, e], {
                    state: i.state,
                    previousState: d
                }), s.html(g.contents);
                var b = s.find("input[autofocus], textarea[autofocus]").last()[0];
                if (b && document.activeElement !== b && b.focus(), v(g.scripts), "number" == typeof e.scrollTo && t(window).scrollTop(e.scrollTo), "" !== o) {
                    var w = f(g.url);
                    w.hash = o, i.state.url = w.href, window.history.replaceState(i.state, g.title, w.href);
                    var x = t(w.hash);
                    x.length && t(window).scrollTop(x.offset().top)
                }
                n("pjax:success", [r, u, c, e])
            }, i.state || (i.state = {
                id: l(),
                url: window.location.href,
                title: document.title,
                container: s.selector,
                fragment: e.fragment,
                timeout: e.timeout
            }, window.history.replaceState(i.state, document.title));
            var d = i.xhr;
            d && d.readyState < 4 && (d.onreadystatechange = t.noop, d.abort()), i.options = e;
            var d = i.xhr = t.ajax(e);
            return d.readyState > 0 && (e.push && !e.replace && (y(i.state.id, s.clone().contents()), window.history.pushState(null, "", c(e.requestUrl))), n("pjax:start", [d, e]), n("pjax:send", [d, e])), i.xhr
        }

        function o(e, n) {
            var r = {
                url: window.location.href,
                push: !1,
                replace: !0,
                scrollTo: !1
            };
            return i(t.extend(r, d(e, n)))
        }

        function a(t) {
            window.history.replaceState(null, "", "#"), window.location.replace(t)
        }

        function s(e) {
            var n = i.state,
                r = e.state;
            if (r && r.container) {
                if (C && k == r.url) return;
                if (i.state && i.state.id === r.id) return;
                var o = t(r.container);
                if (o.length) {
                    var s, u = S[r.id];
                    i.state && (s = i.state.id < r.id ? "forward" : "back", b(s, i.state.id, o.clone().contents()));
                    var l = t.Event("pjax:popstate", {
                        state: r,
                        direction: s
                    });
                    o.trigger(l);
                    var c = {
                        id: r.id,
                        url: r.url,
                        container: o,
                        push: !1,
                        fragment: r.fragment,
                        timeout: r.timeout,
                        scrollTo: !1
                    };
                    if (u) {
                        o.trigger("pjax:start", [null, c]), i.state = r, r.title && (document.title = r.title);
                        var f = t.Event("pjax:beforeReplace", {
                            state: r,
                            previousState: n
                        });
                        o.trigger(f, [u, c]), o.html(u), o.trigger("pjax:end", [null, c])
                    } else i(c);
                    o[0].offsetHeight
                } else a(location.href)
            }
            C = !1
        }

        function u(e) {
            var n = t.isFunction(e.url) ? e.url() : e.url,
                r = e.type ? e.type.toUpperCase() : "GET",
                i = t("<form>", {
                    method: "GET" === r ? "GET" : "POST",
                    action: n,
                    style: "display:none"
                });
            "GET" !== r && "POST" !== r && i.append(t("<input>", {
                type: "hidden",
                name: "_method",
                value: r.toLowerCase()
            }));
            var o = e.data;
            if ("string" == typeof o) t.each(o.split("&"), function(e, n) {
                var r = n.split("=");
                i.append(t("<input>", {
                    type: "hidden",
                    name: r[0],
                    value: r[1]
                }))
            });
            else if ("object" == typeof o)
                for (key in o) i.append(t("<input>", {
                    type: "hidden",
                    name: key,
                    value: o[key]
                }));
            t(document.body).append(i), i.submit()
        }

        function l() {
            return (new Date).getTime()
        }

        function c(t) {
            return t.replace(/\?_pjax=[^&]+&?/, "?").replace(/_pjax=[^&]+&?/, "").replace(/[\?&]$/, "")
        }

        function f(t) {
            var e = document.createElement("a");
            return e.href = t, e
        }

        function d(e, n) {
            return e && n ? n.container = e : n = t.isPlainObject(e) ? e : {
                container: e
            }, n.container && (n.container = p(n.container)), n
        }

        function p(e) {
            if (e = t(e), e.length) {
                if ("" !== e.selector && e.context === document) return e;
                if (e.attr("id")) return t("#" + e.attr("id"));
                throw "cant get selector for pjax container!"
            }
            throw "no pjax container for " + e.selector
        }

        function h(t, e) {
            return t.filter(e).add(t.find(e))
        }

        function g(e) {
            return t.parseHTML(e, document, !0)
        }

        function m(e, n, r) {
            var i = {};
            if (i.url = c(n.getResponseHeader("X-PJAX-URL") || r.requestUrl), /<html/i.test(e)) var o = t(g(e.match(/<head[^>]*>([\s\S.]*)<\/head>/i)[0])),
                a = t(g(e.match(/<body[^>]*>([\s\S.]*)<\/body>/i)[0]));
            else var o = a = t(g(e));
            if (0 === a.length) return i;
            if (i.title = h(o, "title").last().text(), r.fragment) {
                if ("body" === r.fragment) var s = a;
                else var s = h(a, r.fragment).first();
                s.length && (i.contents = s.contents(), i.title || (i.title = s.attr("title") || s.data("title")))
            } else /<html/i.test(e) || (i.contents = a);
            return i.contents && (i.contents = i.contents.not(function() {
                return t(this).is("title")
            }), i.contents.find("title").remove(), i.scripts = h(i.contents, "script[src]").remove(), i.contents = i.contents.not(i.scripts)), i.title && (i.title = t.trim(i.title)), i
        }

        function v(e) {
            if (e) {
                var n = t("script[src]");
                e.each(function() {
                    var e = this.src,
                        r = n.filter(function() {
                            return this.src === e
                        });
                    if (!r.length) {
                        var i = document.createElement("script");
                        i.type = t(this).attr("type"), i.src = t(this).attr("src"), document.head.appendChild(i)
                    }
                })
            }
        }

        function y(t, e) {
            for (S[t] = e, E.push(t); j.length;) delete S[j.shift()];
            for (; E.length > i.defaults.maxCacheLength;) delete S[E.shift()]
        }

        function b(t, e, n) {
            var r, i;
            S[e] = n, "forward" === t ? (r = E, i = j) : (r = j, i = E), r.push(e), (e = i.pop()) && delete S[e]
        }

        function w() {
            return t("meta").filter(function() {
                var e = t(this).attr("http-equiv");
                return e && "X-PJAX-VERSION" === e.toUpperCase()
            }).attr("content")
        }

        function x() {
            t.fn.pjax = e, t.pjax = i, t.pjax.enable = t.noop, t.pjax.disable = _, t.pjax.click = n, t.pjax.submit = r, t.pjax.reload = o, t.pjax.defaults = {
                timeout: 650,
                push: !0,
                replace: !1,
                type: "GET",
                dataType: "html",
                scrollTo: 0,
                maxCacheLength: 20,
                version: w
            }, t(window).on("popstate.pjax", s)
        }

        function _() {
            t.fn.pjax = function() {
                return this
            }, t.pjax = u, t.pjax.enable = x, t.pjax.disable = t.noop, t.pjax.click = t.noop, t.pjax.submit = t.noop, t.pjax.reload = function() {
                window.location.reload()
            }, t(window).off("popstate.pjax", s)
        }
        var C = !0,
            k = window.location.href,
            T = window.history.state;
        T && T.container && (i.state = T), "state" in window.history && (C = !1);
        var S = {},
            j = [],
            E = [];
        t.inArray("state", t.event.props) < 0 && t.event.props.push("state"), t.support.pjax = window.history && window.history.pushState && window.history.replaceState && !navigator.userAgent.match(/((iPod|iPhone|iPad).+\bOS\s+[1-4]|WebApps\/.+CFNetwork)/), t.support.pjax ? x() : _()
    }(jQuery), function(t) {
        "function" == typeof define && define.amd ? define(["jquery"], t) : t(window.jQuery || window.Zepto)
    }(function(t) {
        "use strict";
        var e = function(e, n, r) {
            var i, o, a = this;
            e = t(e), n = "function" == typeof n ? n(e.val(), void 0, e, r) : n, a.init = function() {
                r = r || {}, a.byPassKeys = [9, 16, 17, 18, 36, 37, 38, 39, 40, 91], a.translation = {
                    0: {
                        pattern: /\d/
                    },
                    9: {
                        pattern: /\d/,
                        optional: !0
                    },
                    "#": {
                        pattern: /\d/,
                        recursive: !0
                    },
                    A: {
                        pattern: /[a-zA-Z0-9]/
                    },
                    S: {
                        pattern: /[a-zA-Z]/
                    }
                }, a.translation = t.extend({}, a.translation, r.translation), a = t.extend(!0, {}, a, r), o = s.getRegexMask(), e.each(function() {
                    r.maxlength !== !1 && e.attr("maxlength", n.length), r.placeholder && e.attr("placeholder", r.placeholder), e.attr("autocomplete", "off"), s.destroyEvents(), s.events();
                    var t = s.getCaret();
                    s.val(s.getMasked()), s.setCaret(t + s.getMaskCharactersBeforeCount(t, !0))
                })
            };
            var s = {
                getCaret: function() {
                    var t, n = 0,
                        r = e.get(0),
                        i = document.selection,
                        o = r.selectionStart;
                    return i && !~navigator.appVersion.indexOf("MSIE 10") ? (t = i.createRange(), t.moveStart("character", e.is("input") ? -e.val().length : -e.text().length), n = t.text.length) : (o || "0" === o) && (n = o), n
                },
                setCaret: function(t) {
                    if (e.is(":focus")) {
                        var n, r = e.get(0);
                        r.setSelectionRange ? r.setSelectionRange(t, t) : r.createTextRange && (n = r.createTextRange(), n.collapse(!0), n.moveEnd("character", t), n.moveStart("character", t), n.select())
                    }
                },
                events: function() {
                    e.on("keydown.mask", function() {
                        i = s.val()
                    }), e.on("keyup.mask", s.behaviour), e.on("paste.mask drop.mask", function() {
                        setTimeout(function() {
                            e.keydown().keyup()
                        }, 100)
                    }), e.on("change.mask", function() {
                        e.data("changeCalled", !0)
                    }), e.on("blur.mask", function(e) {
                        var n = t(e.target);
                        n.prop("defaultValue") !== n.val() && (n.prop("defaultValue", n.val()), n.data("changeCalled") || n.trigger("change")), n.data("changeCalled", !1)
                    }), e.on("focusout.mask", function() {
                        r.clearIfNotMatch && !o.test(s.val()) && s.val("")
                    })
                },
                getRegexMask: function() {
                    for (var t, e, r, i, o, s, u = [], l = 0; l < n.length; l++) t = a.translation[n[l]], t ? (e = t.pattern.toString().replace(/.{1}$|^.{1}/g, ""), r = t.optional, i = t.recursive, i ? (u.push(n[l]), o = {
                        digit: n[l],
                        pattern: e
                    }) : u.push(r || i ? e + "?" : e)) : u.push("\\" + n[l]);
                    return s = u.join(""), o && (s = s.replace(new RegExp("(" + o.digit + "(.*" + o.digit + ")?)"), "($1)?").replace(new RegExp(o.digit, "g"), o.pattern)), new RegExp(s)
                },
                destroyEvents: function() {
                    e.off("keydown.mask keyup.mask paste.mask drop.mask change.mask blur.mask focusout.mask").removeData("changeCalled")
                },
                val: function(t) {
                    var n = e.is("input");
                    return arguments.length > 0 ? n ? e.val(t) : e.text(t) : n ? e.val() : e.text()
                },
                getMaskCharactersBeforeCount: function(t, e) {
                    for (var r = 0, i = 0, o = n.length; o > i && t > i; i++) a.translation[n.charAt(i)] || (t = e ? t + 1 : t, r++);
                    return r
                },
                determineCaretPos: function(t, e, r, i) {
                    var o = a.translation[n.charAt(Math.min(t - 1, n.length - 1))];
                    return o ? Math.min(t + r - e - i, r) : s.determineCaretPos(t + 1, e, r, i)
                },
                behaviour: function(e) {
                    e = e || window.event;
                    var n = e.keyCode || e.which;
                    if (-1 === t.inArray(n, a.byPassKeys)) {
                        var r = s.getCaret(),
                            i = s.val(),
                            o = i.length,
                            u = o > r,
                            l = s.getMasked(),
                            c = l.length,
                            f = s.getMaskCharactersBeforeCount(c - 1) - s.getMaskCharactersBeforeCount(o - 1);
                        return l !== i && s.val(l), !u || 65 === n && e.ctrlKey || (8 !== n && 46 !== n && (r = s.determineCaretPos(r, o, c, f)), s.setCaret(r)), s.callbacks(e)
                    }
                },
                getMasked: function(t) {
                    var e, i, o = [],
                        u = s.val(),
                        l = 0,
                        c = n.length,
                        f = 0,
                        d = u.length,
                        p = 1,
                        h = "push",
                        g = -1;
                    for (r.reverse ? (h = "unshift", p = -1, e = 0, l = c - 1, f = d - 1, i = function() {
                            return l > -1 && f > -1
                        }) : (e = c - 1, i = function() {
                            return c > l && d > f
                        }); i();) {
                        var m = n.charAt(l),
                            v = u.charAt(f),
                            y = a.translation[m];
                        y ? (v.match(y.pattern) ? (o[h](v), y.recursive && (-1 === g ? g = l : l === e && (l = g - p), e === g && (l -= p)), l += p) : y.optional && (l += p, f -= p), f += p) : (t || o[h](m), v === m && (f += p), l += p)
                    }
                    var b = n.charAt(e);
                    return c !== d + 1 || a.translation[b] || o.push(b), o.join("")
                },
                callbacks: function(t) {
                    var o = s.val(),
                        a = s.val() !== i;
                    a === !0 && "function" == typeof r.onChange && r.onChange(o, t, e, r), a === !0 && "function" == typeof r.onKeyPress && r.onKeyPress(o, t, e, r), "function" == typeof r.onComplete && o.length === n.length && r.onComplete(o, t, e, r)
                }
            };
            a.remove = function() {
                var t = s.getCaret(),
                    e = s.getMaskCharactersBeforeCount(t);
                s.destroyEvents(), s.val(a.getCleanVal()).removeAttr("maxlength"), s.setCaret(t - e)
            }, a.getCleanVal = function() {
                return s.getMasked(!0)
            }, a.init()
        };
        t.fn.mask = function(n, r) {
            return this.unmask(), this.each(function() {
                t(this).data("mask", new e(this, n, r))
            })
        }, t.fn.unmask = function() {
            return this.each(function() {
                try {
                    t(this).data("mask").remove()
                } catch (e) {}
            })
        }, t.fn.cleanVal = function() {
            return t(this).data("mask").getCleanVal()
        }, t("*[data-mask]").each(function() {
            var e = t(this),
                n = {},
                r = "data-mask-";
            "true" === e.attr(r + "reverse") && (n.reverse = !0), "false" === e.attr(r + "maxlength") && (n.maxlength = !1), "true" === e.attr(r + "clearifnotmatch") && (n.clearIfNotMatch = !0), e.mask(e.attr("data-mask"), n)
        })
    }), function(t, e, n) {
        ! function(t) {
            "use strict";
            "function" == typeof define && define.amd ? define(["jquery"], t) : jQuery && !jQuery.fn.qtip && t(jQuery)
        }(function(r) {
            "use strict";

            function i(t, e, n, i) {
                this.id = n, this.target = t, this.tooltip = T, this.elements = {
                    target: t
                }, this._id = I + "-" + n, this.timers = {
                    img: {}
                }, this.options = e, this.plugins = {}, this.cache = {
                    event: {},
                    target: r(),
                    disabled: k,
                    attr: i,
                    onTooltip: k,
                    lastClass: ""
                }, this.rendered = this.destroyed = this.disabled = this.waiting = this.hiddenDuringWait = this.positioning = this.triggering = k
            }

            function o(t) {
                return t === T || "object" !== r.type(t)
            }

            function a(t) {
                return !(r.isFunction(t) || t && t.attr || t.length || "object" === r.type(t) && (t.jquery || t.then))
            }

            function s(t) {
                var e, n, i, s;
                return o(t) ? k : (o(t.metadata) && (t.metadata = {
                    type: t.metadata
                }), "content" in t && (e = t.content, o(e) || e.jquery || e.done ? e = t.content = {
                    text: n = a(e) ? k : e
                } : n = e.text, "ajax" in e && (i = e.ajax, s = i && i.once !== k, delete e.ajax, e.text = function(t, e) {
                    var o = n || r(this).attr(e.options.content.attr) || "Loading...",
                        a = r.ajax(r.extend({}, i, {
                            context: e
                        })).then(i.success, T, i.error).then(function(t) {
                            return t && s && e.set("content.text", t), t
                        }, function(t, n, r) {
                            e.destroyed || 0 === t.status || e.set("content.text", n + ": " + r)
                        });
                    return s ? o : (e.set("content.text", o), a)
                }), "title" in e && (r.isPlainObject(e.title) && (e.button = e.title.button, e.title = e.title.text), a(e.title || k) && (e.title = k))), "position" in t && o(t.position) && (t.position = {
                    my: t.position,
                    at: t.position
                }), "show" in t && o(t.show) && (t.show = t.show.jquery ? {
                    target: t.show
                } : t.show === C ? {
                    ready: C
                } : {
                    event: t.show
                }), "hide" in t && o(t.hide) && (t.hide = t.hide.jquery ? {
                    target: t.hide
                } : {
                    event: t.hide
                }), "style" in t && o(t.style) && (t.style = {
                    classes: t.style
                }), r.each(D, function() {
                    this.sanitize && this.sanitize(t)
                }), t)
            }

            function u(t, e) {
                for (var n, r = 0, i = t, o = e.split("."); i = i[o[r++]];) r < o.length && (n = i);
                return [n || t, o.pop()]
            }

            function l(t, e) {
                var n, r, i;
                for (n in this.checks)
                    for (r in this.checks[n])(i = new RegExp(r, "i").exec(t)) && (e.push(i), ("builtin" === n || this.plugins[n]) && this.checks[n][r].apply(this.plugins[n] || this, e))
            }

            function c(t) {
                return R.concat("").join(t ? "-" + t + " " : " ")
            }

            function f(t, e) {
                return e > 0 ? setTimeout(r.proxy(t, this), e) : void t.call(this)
            }

            function d(t) {
                this.tooltip.hasClass(W) || (clearTimeout(this.timers.show), clearTimeout(this.timers.hide), this.timers.show = f.call(this, function() {
                    this.toggle(C, t)
                }, this.options.show.delay))
            }

            function p(t) {
                if (!this.tooltip.hasClass(W) && !this.destroyed) {
                    var e = r(t.relatedTarget),
                        n = e.closest(q)[0] === this.tooltip[0],
                        i = e[0] === this.options.show.target[0];
                    if (clearTimeout(this.timers.show), clearTimeout(this.timers.hide), this !== e[0] && "mouse" === this.options.position.target && n || this.options.hide.fixed && /mouse(out|leave|move)/.test(t.type) && (n || i)) try {
                        t.preventDefault(), t.stopImmediatePropagation()
                    } catch (o) {} else this.timers.hide = f.call(this, function() {
                        this.toggle(k, t)
                    }, this.options.hide.delay, this)
                }
            }

            function h(t) {
                !this.tooltip.hasClass(W) && this.options.hide.inactive && (clearTimeout(this.timers.inactive), this.timers.inactive = f.call(this, function() {
                    this.hide(t)
                }, this.options.hide.inactive))
            }

            function g(t) {
                this.rendered && this.tooltip[0].offsetWidth > 0 && this.reposition(t)
            }

            function m(t, n, i) {
                r(e.body).delegate(t, (n.split ? n : n.join("." + I + " ")) + "." + I, function() {
                    var t = y.api[r.attr(this, F)];
                    t && !t.disabled && i.apply(t, arguments)
                })
            }

            function v(t, n, o) {
                var a, u, l, c, f, d = r(e.body),
                    p = t[0] === e ? d : t,
                    h = t.metadata ? t.metadata(o.metadata) : T,
                    g = "html5" === o.metadata.type && h ? h[o.metadata.name] : T,
                    m = t.data(o.metadata.name || "qtipopts");
                try {
                    m = "string" == typeof m ? r.parseJSON(m) : m
                } catch (v) {}
                if (c = r.extend(C, {}, y.defaults, o, "object" == typeof m ? s(m) : T, s(g || h)), u = c.position, c.id = n, "boolean" == typeof c.content.text) {
                    if (l = t.attr(c.content.attr), c.content.attr === k || !l) return k;
                    c.content.text = l
                }
                if (u.container.length || (u.container = d), u.target === k && (u.target = p), c.show.target === k && (c.show.target = p), c.show.solo === C && (c.show.solo = u.container.closest("body")), c.hide.target === k && (c.hide.target = p), c.position.viewport === C && (c.position.viewport = u.container), u.container = u.container.eq(0), u.at = new w(u.at, C), u.my = new w(u.my), t.data(I))
                    if (c.overwrite) t.qtip("destroy", !0);
                    else if (c.overwrite === k) return k;
                return t.attr(L, n), c.suppress && (f = t.attr("title")) && t.removeAttr("title").attr(V, f).attr("title", ""), a = new i(t, c, n, !!l), t.data(I, a), a
            }
            var y, b, w, x, _, C = !0,
                k = !1,
                T = null,
                S = "x",
                j = "y",
                E = "top",
                N = "left",
                A = "bottom",
                $ = "right",
                O = "center",
                D = {},
                I = "qtip",
                L = "data-hasqtip",
                F = "data-qtip-id",
                R = ["ui-widget", "ui-tooltip"],
                q = "." + I,
                M = "click dblclick mousedown mouseup mousemove mouseleave mouseenter".split(" "),
                P = I + "-fixed",
                z = I + "-default",
                H = I + "-focus",
                B = I + "-hover",
                W = I + "-disabled",
                U = "_replacedByqTip",
                V = "oldtitle",
                K = {
                    ie: function() {
                        for (var t = 4, n = e.createElement("div");
                            (n.innerHTML = "<!--[if gt IE " + t + "]><i></i><![endif]-->") && n.getElementsByTagName("i")[0]; t += 1);
                        return t > 4 ? t : 0 / 0
                    }(),
                    iOS: parseFloat(("" + (/CPU.*OS ([0-9_]{1,5})|(CPU like).*AppleWebKit.*Mobile/i.exec(navigator.userAgent) || [0, ""])[1]).replace("undefined", "3_2").replace("_", ".").replace("_", "")) || k
                };
            b = i.prototype, b._when = function(t) {
                return r.when.apply(r, t)
            }, b.render = function(t) {
                if (this.rendered || this.destroyed) return this;
                var e, n = this,
                    i = this.options,
                    o = this.cache,
                    a = this.elements,
                    s = i.content.text,
                    u = i.content.title,
                    l = i.content.button,
                    c = i.position,
                    f = ("." + this._id + " ", []);
                return r.attr(this.target[0], "aria-describedby", this._id), o.posClass = this._createPosClass((this.position = {
                    my: c.my,
                    at: c.at
                }).my), this.tooltip = a.tooltip = e = r("<div/>", {
                    id: this._id,
                    "class": [I, z, i.style.classes, o.posClass].join(" "),
                    width: i.style.width || "",
                    height: i.style.height || "",
                    tracking: "mouse" === c.target && c.adjust.mouse,
                    role: "alert",
                    "aria-live": "polite",
                    "aria-atomic": k,
                    "aria-describedby": this._id + "-content",
                    "aria-hidden": C
                }).toggleClass(W, this.disabled).attr(F, this.id).data(I, this).appendTo(c.container).append(a.content = r("<div />", {
                    "class": I + "-content",
                    id: this._id + "-content",
                    "aria-atomic": C
                })), this.rendered = -1, this.positioning = C, u && (this._createTitle(), r.isFunction(u) || f.push(this._updateTitle(u, k))), l && this._createButton(), r.isFunction(s) || f.push(this._updateContent(s, k)), this.rendered = C, this._setWidget(), r.each(D, function(t) {
                    var e;
                    "render" === this.initialize && (e = this(n)) && (n.plugins[t] = e)
                }), this._unassignEvents(), this._assignEvents(), this._when(f).then(function() {
                    n._trigger("render"), n.positioning = k, n.hiddenDuringWait || !i.show.ready && !t || n.toggle(C, o.event, k), n.hiddenDuringWait = k
                }), y.api[this.id] = this, this
            }, b.destroy = function(t) {
                function e() {
                    if (!this.destroyed) {
                        this.destroyed = C;
                        var t, e = this.target,
                            n = e.attr(V);
                        this.rendered && this.tooltip.stop(1, 0).find("*").remove().end().remove(), r.each(this.plugins, function() {
                            this.destroy && this.destroy()
                        });
                        for (t in this.timers) clearTimeout(this.timers[t]);
                        e.removeData(I).removeAttr(F).removeAttr(L).removeAttr("aria-describedby"), this.options.suppress && n && e.attr("title", n).removeAttr(V), this._unassignEvents(), this.options = this.elements = this.cache = this.timers = this.plugins = this.mouse = T, delete y.api[this.id]
                    }
                }
                return this.destroyed ? this.target : (t === C && "hide" !== this.triggering || !this.rendered ? e.call(this) : (this.tooltip.one("tooltiphidden", r.proxy(e, this)), !this.triggering && this.hide()), this.target)
            }, x = b.checks = {
                builtin: {
                    "^id$": function(t, e, n, i) {
                        var o = n === C ? y.nextid : n,
                            a = I + "-" + o;
                        o !== k && o.length > 0 && !r("#" + a).length ? (this._id = a, this.rendered && (this.tooltip[0].id = this._id, this.elements.content[0].id = this._id + "-content", this.elements.title[0].id = this._id + "-title")) : t[e] = i
                    },
                    "^prerender": function(t, e, n) {
                        n && !this.rendered && this.render(this.options.show.ready)
                    },
                    "^content.text$": function(t, e, n) {
                        this._updateContent(n)
                    },
                    "^content.attr$": function(t, e, n, r) {
                        this.options.content.text === this.target.attr(r) && this._updateContent(this.target.attr(n))
                    },
                    "^content.title$": function(t, e, n) {
                        return n ? (n && !this.elements.title && this._createTitle(), void this._updateTitle(n)) : this._removeTitle()
                    },
                    "^content.button$": function(t, e, n) {
                        this._updateButton(n)
                    },
                    "^content.title.(text|button)$": function(t, e, n) {
                        this.set("content." + e, n)
                    },
                    "^position.(my|at)$": function(t, e, n) {
                        "string" == typeof n && (this.position[e] = t[e] = new w(n, "at" === e))
                    },
                    "^position.container$": function(t, e, n) {
                        this.rendered && this.tooltip.appendTo(n)
                    },
                    "^show.ready$": function(t, e, n) {
                        n && (!this.rendered && this.render(C) || this.toggle(C))
                    },
                    "^style.classes$": function(t, e, n, r) {
                        this.rendered && this.tooltip.removeClass(r).addClass(n)
                    },
                    "^style.(width|height)": function(t, e, n) {
                        this.rendered && this.tooltip.css(e, n)
                    },
                    "^style.widget|content.title": function() {
                        this.rendered && this._setWidget()
                    },
                    "^style.def": function(t, e, n) {
                        this.rendered && this.tooltip.toggleClass(z, !!n)
                    },
                    "^events.(render|show|move|hide|focus|blur)$": function(t, e, n) {
                        this.rendered && this.tooltip[(r.isFunction(n) ? "" : "un") + "bind"]("tooltip" + e, n)
                    },
                    "^(show|hide|position).(event|target|fixed|inactive|leave|distance|viewport|adjust)": function() {
                        if (this.rendered) {
                            var t = this.options.position;
                            this.tooltip.attr("tracking", "mouse" === t.target && t.adjust.mouse), this._unassignEvents(), this._assignEvents()
                        }
                    }
                }
            }, b.get = function(t) {
                if (this.destroyed) return this;
                var e = u(this.options, t.toLowerCase()),
                    n = e[0][e[1]];
                return n.precedance ? n.string() : n
            };
            var X = /^position\.(my|at|adjust|target|container|viewport)|style|content|show\.ready/i,
                Q = /^prerender|show\.ready/i;
            b.set = function(t, e) {
                if (this.destroyed) return this; {
                    var n, i = this.rendered,
                        o = k,
                        a = this.options;
                    this.checks
                }
                return "string" == typeof t ? (n = t, t = {}, t[n] = e) : t = r.extend({}, t), r.each(t, function(e, n) {
                    if (i && Q.test(e)) return void delete t[e];
                    var s, l = u(a, e.toLowerCase());
                    s = l[0][l[1]], l[0][l[1]] = n && n.nodeType ? r(n) : n, o = X.test(e) || o, t[e] = [l[0], l[1], n, s]
                }), s(a), this.positioning = C, r.each(t, r.proxy(l, this)), this.positioning = k, this.rendered && this.tooltip[0].offsetWidth > 0 && o && this.reposition("mouse" === a.position.target ? T : this.cache.event), this
            }, b._update = function(t, e) {
                var n = this,
                    i = this.cache;
                return this.rendered && t ? (r.isFunction(t) && (t = t.call(this.elements.target, i.event, this) || ""), r.isFunction(t.then) ? (i.waiting = C, t.then(function(t) {
                    return i.waiting = k, n._update(t, e)
                }, T, function(t) {
                    return n._update(t, e)
                })) : t === k || !t && "" !== t ? k : (t.jquery && t.length > 0 ? e.empty().append(t.css({
                    display: "block",
                    visibility: "visible"
                })) : e.html(t), this._waitForContent(e).then(function(t) {
                    n.rendered && n.tooltip[0].offsetWidth > 0 && n.reposition(i.event, !t.length)
                }))) : k
            }, b._waitForContent = function(t) {
                var e = this.cache;
                return e.waiting = C, (r.fn.imagesLoaded ? t.imagesLoaded() : r.Deferred().resolve([])).done(function() {
                    e.waiting = k
                }).promise()
            }, b._updateContent = function(t, e) {
                this._update(t, this.elements.content, e)
            }, b._updateTitle = function(t, e) {
                this._update(t, this.elements.title, e) === k && this._removeTitle(k)
            }, b._createTitle = function() {
                var t = this.elements,
                    e = this._id + "-title";
                t.titlebar && this._removeTitle(), t.titlebar = r("<div />", {
                    "class": I + "-titlebar " + (this.options.style.widget ? c("header") : "")
                }).append(t.title = r("<div />", {
                    id: e,
                    "class": I + "-title",
                    "aria-atomic": C
                })).insertBefore(t.content).delegate(".qtip-close", "mousedown keydown mouseup keyup mouseout", function(t) {
                    r(this).toggleClass("ui-state-active ui-state-focus", "down" === t.type.substr(-4))
                }).delegate(".qtip-close", "mouseover mouseout", function(t) {
                    r(this).toggleClass("ui-state-hover", "mouseover" === t.type)
                }), this.options.content.button && this._createButton()
            }, b._removeTitle = function(t) {
                var e = this.elements;
                e.title && (e.titlebar.remove(), e.titlebar = e.title = e.button = T, t !== k && this.reposition())
            }, b._createPosClass = function(t) {
                return I + "-pos-" + (t || this.options.position.my).abbrev()
            }, b.reposition = function(n, i) {
                if (!this.rendered || this.positioning || this.destroyed) return this;
                this.positioning = C;
                var o, a, s, u, l = this.cache,
                    c = this.tooltip,
                    f = this.options.position,
                    d = f.target,
                    p = f.my,
                    h = f.at,
                    g = f.viewport,
                    m = f.container,
                    v = f.adjust,
                    y = v.method.split(" "),
                    b = c.outerWidth(k),
                    w = c.outerHeight(k),
                    x = 0,
                    _ = 0,
                    T = c.css("position"),
                    S = {
                        left: 0,
                        top: 0
                    },
                    j = c[0].offsetWidth > 0,
                    I = n && "scroll" === n.type,
                    L = r(t),
                    F = m[0].ownerDocument,
                    R = this.mouse;
                if (r.isArray(d) && 2 === d.length) h = {
                    x: N,
                    y: E
                }, S = {
                    left: d[0],
                    top: d[1]
                };
                else if ("mouse" === d) h = {
                    x: N,
                    y: E
                }, (!v.mouse || this.options.hide.distance) && l.origin && l.origin.pageX ? n = l.origin : !n || n && ("resize" === n.type || "scroll" === n.type) ? n = l.event : R && R.pageX && (n = R), "static" !== T && (S = m.offset()), F.body.offsetWidth !== (t.innerWidth || F.documentElement.clientWidth) && (a = r(e.body).offset()), S = {
                    left: n.pageX - S.left + (a && a.left || 0),
                    top: n.pageY - S.top + (a && a.top || 0)
                }, v.mouse && I && R && (S.left -= (R.scrollX || 0) - L.scrollLeft(), S.top -= (R.scrollY || 0) - L.scrollTop());
                else {
                    if ("event" === d ? n && n.target && "scroll" !== n.type && "resize" !== n.type ? l.target = r(n.target) : n.target || (l.target = this.elements.target) : "event" !== d && (l.target = r(d.jquery ? d : this.elements.target)), d = l.target, d = r(d).eq(0), 0 === d.length) return this;
                    d[0] === e || d[0] === t ? (x = K.iOS ? t.innerWidth : d.width(), _ = K.iOS ? t.innerHeight : d.height(), d[0] === t && (S = {
                        top: (g || d).scrollTop(),
                        left: (g || d).scrollLeft()
                    })) : D.imagemap && d.is("area") ? o = D.imagemap(this, d, h, D.viewport ? y : k) : D.svg && d && d[0].ownerSVGElement ? o = D.svg(this, d, h, D.viewport ? y : k) : (x = d.outerWidth(k), _ = d.outerHeight(k), S = d.offset()), o && (x = o.width, _ = o.height, a = o.offset, S = o.position), S = this.reposition.offset(d, S, m), (K.iOS > 3.1 && K.iOS < 4.1 || K.iOS >= 4.3 && K.iOS < 4.33 || !K.iOS && "fixed" === T) && (S.left -= L.scrollLeft(), S.top -= L.scrollTop()), (!o || o && o.adjustable !== k) && (S.left += h.x === $ ? x : h.x === O ? x / 2 : 0, S.top += h.y === A ? _ : h.y === O ? _ / 2 : 0)
                }
                return S.left += v.x + (p.x === $ ? -b : p.x === O ? -b / 2 : 0), S.top += v.y + (p.y === A ? -w : p.y === O ? -w / 2 : 0), D.viewport ? (s = S.adjusted = D.viewport(this, S, f, x, _, b, w), a && s.left && (S.left += a.left), a && s.top && (S.top += a.top), s.my && (this.position.my = s.my)) : S.adjusted = {
                    left: 0,
                    top: 0
                }, l.posClass !== (u = this._createPosClass(this.position.my)) && c.removeClass(l.posClass).addClass(l.posClass = u), this._trigger("move", [S, g.elem || g], n) ? (delete S.adjusted, i === k || !j || isNaN(S.left) || isNaN(S.top) || "mouse" === d || !r.isFunction(f.effect) ? c.css(S) : r.isFunction(f.effect) && (f.effect.call(c, this, r.extend({}, S)), c.queue(function(t) {
                    r(this).css({
                        opacity: "",
                        height: ""
                    }), K.ie && this.style.removeAttribute("filter"), t()
                })), this.positioning = k, this) : this
            }, b.reposition.offset = function(t, n, i) {
                function o(t, e) {
                    n.left += e * t.scrollLeft(), n.top += e * t.scrollTop()
                }
                if (!i[0]) return n;
                var a, s, u, l, c = r(t[0].ownerDocument),
                    f = !!K.ie && "CSS1Compat" !== e.compatMode,
                    d = i[0];
                do "static" !== (s = r.css(d, "position")) && ("fixed" === s ? (u = d.getBoundingClientRect(), o(c, -1)) : (u = r(d).position(), u.left += parseFloat(r.css(d, "borderLeftWidth")) || 0, u.top += parseFloat(r.css(d, "borderTopWidth")) || 0), n.left -= u.left + (parseFloat(r.css(d, "marginLeft")) || 0), n.top -= u.top + (parseFloat(r.css(d, "marginTop")) || 0), a || "hidden" === (l = r.css(d, "overflow")) || "visible" === l || (a = r(d))); while (d = d.offsetParent);
                return a && (a[0] !== c[0] || f) && o(a, 1), n
            };
            var G = (w = b.reposition.Corner = function(t, e) {
                t = ("" + t).replace(/([A-Z])/, " $1").replace(/middle/gi, O).toLowerCase(), this.x = (t.match(/left|right/i) || t.match(/center/) || ["inherit"])[0].toLowerCase(), this.y = (t.match(/top|bottom|center/i) || ["inherit"])[0].toLowerCase(), this.forceY = !!e;
                var n = t.charAt(0);
                this.precedance = "t" === n || "b" === n ? j : S
            }).prototype;
            G.invert = function(t, e) {
                this[t] = this[t] === N ? $ : this[t] === $ ? N : e || this[t]
            }, G.string = function(t) {
                var e = this.x,
                    n = this.y,
                    r = e !== n ? "center" === e || "center" !== n && (this.precedance === j || this.forceY) ? [n, e] : [e, n] : [e];
                return t !== !1 ? r.join(" ") : r
            }, G.abbrev = function() {
                var t = this.string(!1);
                return t[0].charAt(0) + (t[1] && t[1].charAt(0) || "")
            }, G.clone = function() {
                return new w(this.string(), this.forceY)
            }, b.toggle = function(t, n) {
                var i = this.cache,
                    o = this.options,
                    a = this.tooltip;
                if (n) {
                    if (/over|enter/.test(n.type) && i.event && /out|leave/.test(i.event.type) && o.show.target.add(n.target).length === o.show.target.length && a.has(n.relatedTarget).length) return this;
                    i.event = r.event.fix(n)
                }
                if (this.waiting && !t && (this.hiddenDuringWait = C), !this.rendered) return t ? this.render(1) : this;
                if (this.destroyed || this.disabled) return this;
                var s, u, l, c = t ? "show" : "hide",
                    f = this.options[c],
                    d = (this.options[t ? "hide" : "show"], this.options.position),
                    p = this.options.content,
                    h = this.tooltip.css("width"),
                    g = this.tooltip.is(":visible"),
                    m = t || 1 === f.target.length,
                    v = !n || f.target.length < 2 || i.target[0] === n.target;
                return (typeof t).search("boolean|number") && (t = !g), s = !a.is(":animated") && g === t && v, u = s ? T : !!this._trigger(c, [90]), this.destroyed ? this : (u !== k && t && this.focus(n), !u || s ? this : (r.attr(a[0], "aria-hidden", !t), t ? (this.mouse && (i.origin = r.event.fix(this.mouse)), r.isFunction(p.text) && this._updateContent(p.text, k), r.isFunction(p.title) && this._updateTitle(p.title, k), !_ && "mouse" === d.target && d.adjust.mouse && (r(e).bind("mousemove." + I, this._storeMouse), _ = C), h || a.css("width", a.outerWidth(k)), this.reposition(n, arguments[2]), h || a.css("width", ""), f.solo && ("string" == typeof f.solo ? r(f.solo) : r(q, f.solo)).not(a).not(f.target).qtip("hide", r.Event("tooltipsolo"))) : (clearTimeout(this.timers.show), delete i.origin, _ && !r(q + '[tracking="true"]:visible', f.solo).not(a).length && (r(e).unbind("mousemove." + I), _ = k), this.blur(n)), l = r.proxy(function() {
                    t ? (K.ie && a[0].style.removeAttribute("filter"), a.css("overflow", ""), "string" == typeof f.autofocus && r(this.options.show.autofocus, a).focus(), this.options.show.target.trigger("qtip-" + this.id + "-inactive")) : a.css({
                        display: "",
                        visibility: "",
                        opacity: "",
                        left: "",
                        top: ""
                    }), this._trigger(t ? "visible" : "hidden")
                }, this), f.effect === k || m === k ? (a[c](), l()) : r.isFunction(f.effect) ? (a.stop(1, 1), f.effect.call(a, this), a.queue("fx", function(t) {
                    l(), t()
                })) : a.fadeTo(90, t ? 1 : 0, l), t && f.target.trigger("qtip-" + this.id + "-inactive"), this))
            }, b.show = function(t) {
                return this.toggle(C, t)
            }, b.hide = function(t) {
                return this.toggle(k, t)
            }, b.focus = function(t) {
                if (!this.rendered || this.destroyed) return this;
                var e = r(q),
                    n = this.tooltip,
                    i = parseInt(n[0].style.zIndex, 10),
                    o = y.zindex + e.length;
                return n.hasClass(H) || this._trigger("focus", [o], t) && (i !== o && (e.each(function() {
                    this.style.zIndex > i && (this.style.zIndex = this.style.zIndex - 1)
                }), e.filter("." + H).qtip("blur", t)), n.addClass(H)[0].style.zIndex = o), this
            }, b.blur = function(t) {
                return !this.rendered || this.destroyed ? this : (this.tooltip.removeClass(H), this._trigger("blur", [this.tooltip.css("zIndex")], t), this)
            }, b.disable = function(t) {
                return this.destroyed ? this : ("toggle" === t ? t = !(this.rendered ? this.tooltip.hasClass(W) : this.disabled) : "boolean" != typeof t && (t = C), this.rendered && this.tooltip.toggleClass(W, t).attr("aria-disabled", t), this.disabled = !!t, this)
            }, b.enable = function() {
                return this.disable(k)
            }, b._createButton = function() {
                var t = this,
                    e = this.elements,
                    n = e.tooltip,
                    i = this.options.content.button,
                    o = "string" == typeof i,
                    a = o ? i : "Close tooltip";
                e.button && e.button.remove(), e.button = i.jquery ? i : r("<a />", {
                    "class": "qtip-close " + (this.options.style.widget ? "" : I + "-icon"),
                    title: a,
                    "aria-label": a
                }).prepend(r("<span />", {
                    "class": "ui-icon ui-icon-close",
                    html: "&times;"
                })), e.button.appendTo(e.titlebar || n).attr("role", "button").click(function(e) {
                    return n.hasClass(W) || t.hide(e), k
                })
            }, b._updateButton = function(t) {
                if (!this.rendered) return k;
                var e = this.elements.button;
                t ? this._createButton() : e.remove()
            }, b._setWidget = function() {
                var t = this.options.style.widget,
                    e = this.elements,
                    n = e.tooltip,
                    r = n.hasClass(W);
                n.removeClass(W), W = t ? "ui-state-disabled" : "qtip-disabled", n.toggleClass(W, r), n.toggleClass("ui-helper-reset " + c(), t).toggleClass(z, this.options.style.def && !t), e.content && e.content.toggleClass(c("content"), t), e.titlebar && e.titlebar.toggleClass(c("header"), t), e.button && e.button.toggleClass(I + "-icon", !t)
            }, b._storeMouse = function(t) {
                return (this.mouse = r.event.fix(t)).type = "mousemove", this
            }, b._bind = function(t, e, n, i, o) {
                if (t && n && e.length) {
                    var a = "." + this._id + (i ? "-" + i : "");
                    return r(t).bind((e.split ? e : e.join(a + " ")) + a, r.proxy(n, o || this)), this
                }
            }, b._unbind = function(t, e) {
                return t && r(t).unbind("." + this._id + (e ? "-" + e : "")), this
            }, b._trigger = function(t, e, n) {
                var i = r.Event("tooltip" + t);
                return i.originalEvent = n && r.extend({}, n) || this.cache.event || T, this.triggering = t, this.tooltip.trigger(i, [this].concat(e || [])), this.triggering = k, !i.isDefaultPrevented()
            }, b._bindEvents = function(t, e, n, i, o, a) {
                var s = n.filter(i).add(i.filter(n)),
                    u = [];
                s.length && (r.each(e, function(e, n) {
                    var i = r.inArray(n, t);
                    i > -1 && u.push(t.splice(i, 1)[0])
                }), u.length && (this._bind(s, u, function(t) {
                    var e = this.rendered ? this.tooltip[0].offsetWidth > 0 : !1;
                    (e ? a : o).call(this, t)
                }), n = n.not(s), i = i.not(s))), this._bind(n, t, o), this._bind(i, e, a)
            }, b._assignInitialEvents = function(t) {
                function e(t) {
                    return this.disabled || this.destroyed ? k : (this.cache.event = t && r.event.fix(t), this.cache.target = t && r(t.target), clearTimeout(this.timers.show), void(this.timers.show = f.call(this, function() {
                        this.render("object" == typeof t || n.show.ready)
                    }, n.prerender ? 0 : n.show.delay)))
                }
                var n = this.options,
                    i = n.show.target,
                    o = n.hide.target,
                    a = n.show.event ? r.trim("" + n.show.event).split(" ") : [],
                    s = n.hide.event ? r.trim("" + n.hide.event).split(" ") : [];
                this._bind(this.elements.target, ["remove", "removeqtip"], function() {
                    this.destroy(!0)
                }, "destroy"), /mouse(over|enter)/i.test(n.show.event) && !/mouse(out|leave)/i.test(n.hide.event) && s.push("mouseleave"), this._bind(i, "mousemove", function(t) {
                    this._storeMouse(t), this.cache.onTarget = C
                }), this._bindEvents(a, s, i, o, e, function() {
                    return this.timers ? void clearTimeout(this.timers.show) : k
                }), (n.show.ready || n.prerender) && e.call(this, t)
            }, b._assignEvents = function() {
                var n = this,
                    i = this.options,
                    o = i.position,
                    a = this.tooltip,
                    s = i.show.target,
                    u = i.hide.target,
                    l = o.container,
                    c = o.viewport,
                    f = r(e),
                    m = (r(e.body), r(t)),
                    v = i.show.event ? r.trim("" + i.show.event).split(" ") : [],
                    b = i.hide.event ? r.trim("" + i.hide.event).split(" ") : [];
                r.each(i.events, function(t, e) {
                    n._bind(a, "toggle" === t ? ["tooltipshow", "tooltiphide"] : ["tooltip" + t], e, null, a)
                }), /mouse(out|leave)/i.test(i.hide.event) && "window" === i.hide.leave && this._bind(f, ["mouseout", "blur"], function(t) {
                    /select|option/.test(t.target.nodeName) || t.relatedTarget || this.hide(t)
                }), i.hide.fixed ? u = u.add(a.addClass(P)) : /mouse(over|enter)/i.test(i.show.event) && this._bind(u, "mouseleave", function() {
                    clearTimeout(this.timers.show)
                }), ("" + i.hide.event).indexOf("unfocus") > -1 && this._bind(l.closest("html"), ["mousedown", "touchstart"], function(t) {
                    var e = r(t.target),
                        n = this.rendered && !this.tooltip.hasClass(W) && this.tooltip[0].offsetWidth > 0,
                        i = e.parents(q).filter(this.tooltip[0]).length > 0;
                    e[0] === this.target[0] || e[0] === this.tooltip[0] || i || this.target.has(e[0]).length || !n || this.hide(t)
                }), "number" == typeof i.hide.inactive && (this._bind(s, "qtip-" + this.id + "-inactive", h, "inactive"), this._bind(u.add(a), y.inactiveEvents, h)), this._bindEvents(v, b, s, u, d, p), this._bind(s.add(a), "mousemove", function(t) {
                    if ("number" == typeof i.hide.distance) {
                        var e = this.cache.origin || {},
                            n = this.options.hide.distance,
                            r = Math.abs;
                        (r(t.pageX - e.pageX) >= n || r(t.pageY - e.pageY) >= n) && this.hide(t)
                    }
                    this._storeMouse(t)
                }), "mouse" === o.target && o.adjust.mouse && (i.hide.event && this._bind(s, ["mouseenter", "mouseleave"], function(t) {
                    return this.cache ? void(this.cache.onTarget = "mouseenter" === t.type) : k
                }), this._bind(f, "mousemove", function(t) {
                    this.rendered && this.cache.onTarget && !this.tooltip.hasClass(W) && this.tooltip[0].offsetWidth > 0 && this.reposition(t)
                })), (o.adjust.resize || c.length) && this._bind(r.event.special.resize ? c : m, "resize", g), o.adjust.scroll && this._bind(m.add(o.container), "scroll", g)
            }, b._unassignEvents = function() {
                var n = this.options,
                    i = n.show.target,
                    o = n.hide.target,
                    a = r.grep([this.elements.target[0], this.rendered && this.tooltip[0], n.position.container[0], n.position.viewport[0], n.position.container.closest("html")[0], t, e], function(t) {
                        return "object" == typeof t
                    });
                i && i.toArray && (a = a.concat(i.toArray())), o && o.toArray && (a = a.concat(o.toArray())), this._unbind(a)._unbind(a, "destroy")._unbind(a, "inactive")
            }, r(function() {
                m(q, ["mouseenter", "mouseleave"], function(t) {
                    var e = "mouseenter" === t.type,
                        n = r(t.currentTarget),
                        i = r(t.relatedTarget || t.target),
                        o = this.options;
                    e ? (this.focus(t), n.hasClass(P) && !n.hasClass(W) && clearTimeout(this.timers.hide)) : "mouse" === o.position.target && o.position.adjust.mouse && o.hide.event && o.show.target && !i.closest(o.show.target[0]).length && this.hide(t), n.toggleClass(B, e)
                }), m("[" + F + "]", M, h)
            }), y = r.fn.qtip = function(t, e, i) {
                var o = ("" + t).toLowerCase(),
                    a = T,
                    u = r.makeArray(arguments).slice(1),
                    l = u[u.length - 1],
                    c = this[0] ? r.data(this[0], I) : T;
                return !arguments.length && c || "api" === o ? c : "string" == typeof t ? (this.each(function() {
                    var t = r.data(this, I);
                    if (!t) return C;
                    if (l && l.timeStamp && (t.cache.event = l), !e || "option" !== o && "options" !== o) t[o] && t[o].apply(t, u);
                    else {
                        if (i === n && !r.isPlainObject(e)) return a = t.get(e), k;
                        t.set(e, i)
                    }
                }), a !== T ? a : this) : "object" != typeof t && arguments.length ? void 0 : (c = s(r.extend(C, {}, t)), this.each(function(t) {
                    var e, n;
                    return n = r.isArray(c.id) ? c.id[t] : c.id, n = !n || n === k || n.length < 1 || y.api[n] ? y.nextid++ : n, e = v(r(this), n, c), e === k ? C : (y.api[n] = e, r.each(D, function() {
                        "initialize" === this.initialize && this(e)
                    }), void e._assignInitialEvents(l))
                }))
            }, r.qtip = i, y.api = {}, r.each({
                attr: function(t, e) {
                    if (this.length) {
                        var n = this[0],
                            i = "title",
                            o = r.data(n, "qtip");
                        if (t === i && o && "object" == typeof o && o.options.suppress) return arguments.length < 2 ? r.attr(n, V) : (o && o.options.content.attr === i && o.cache.attr && o.set("content.text", e), this.attr(V, e))
                    }
                    return r.fn["attr" + U].apply(this, arguments)
                },
                clone: function(t) {
                    var e = (r([]), r.fn["clone" + U].apply(this, arguments));
                    return t || e.filter("[" + V + "]").attr("title", function() {
                        return r.attr(this, V)
                    }).removeAttr(V), e
                }
            }, function(t, e) {
                if (!e || r.fn[t + U]) return C;
                var n = r.fn[t + U] = r.fn[t];
                r.fn[t] = function() {
                    return e.apply(this, arguments) || n.apply(this, arguments)
                }
            }), r.ui || (r["cleanData" + U] = r.cleanData, r.cleanData = function(t) {
                for (var e, n = 0;
                    (e = r(t[n])).length; n++)
                    if (e.attr(L)) try {
                        e.triggerHandler("removeqtip")
                    } catch (i) {}
                    r["cleanData" + U].apply(this, arguments)
            }), y.version = "2.2.1", y.nextid = 0, y.inactiveEvents = M, y.zindex = 15e3, y.defaults = {
                prerender: k,
                id: k,
                overwrite: C,
                suppress: C,
                content: {
                    text: C,
                    attr: "title",
                    title: k,
                    button: k
                },
                position: {
                    my: "top left",
                    at: "bottom right",
                    target: k,
                    container: k,
                    viewport: k,
                    adjust: {
                        x: 0,
                        y: 0,
                        mouse: C,
                        scroll: C,
                        resize: C,
                        method: "flipinvert flipinvert"
                    },
                    effect: function(t, e) {
                        r(this).animate(e, {
                            duration: 200,
                            queue: k
                        })
                    }
                },
                show: {
                    target: k,
                    event: "mouseenter",
                    effect: C,
                    delay: 90,
                    solo: k,
                    ready: k,
                    autofocus: k
                },
                hide: {
                    target: k,
                    event: "mouseleave",
                    effect: C,
                    delay: 0,
                    fixed: k,
                    inactive: k,
                    leave: "window",
                    distance: k
                },
                style: {
                    classes: "",
                    widget: k,
                    width: k,
                    height: k,
                    def: C
                },
                events: {
                    render: T,
                    move: T,
                    show: T,
                    hide: T,
                    toggle: T,
                    visible: T,
                    hidden: T,
                    focus: T,
                    blur: T
                }
            }
        })
    }(window, document), function(t) {
        var e = t.fn.ready;
        t.fn.ready = function(n) {
            e(void 0 === this.context ? n : this.selector ? t.proxy(function() {
                t(this.selector, this.context).each(n)
            }, this) : t.proxy(function() {
                t(this).each(n)
            }, this))
        }
    }(jQuery), function(t, e) {
        "function" == typeof define && define.amd ? define("sifter", e) : "object" == typeof exports ? module.exports = e() : t.Sifter = e()
    }(this, function() {
        var t = function(t, e) {
            this.items = t, this.settings = e || {
                diacritics: !0
            }
        };
        t.prototype.tokenize = function(t) {
            if (t = r(String(t || "").toLowerCase()), !t || !t.length) return [];
            var e, n, o, s, u = [],
                l = t.split(/ +/);
            for (e = 0, n = l.length; n > e; e++) {
                if (o = i(l[e]), this.settings.diacritics)
                    for (s in a) a.hasOwnProperty(s) && (o = o.replace(new RegExp(s, "g"), a[s]));
                u.push({
                    string: l[e],
                    regex: new RegExp(o, "i")
                })
            }
            return u
        }, t.prototype.iterator = function(t, e) {
            var n;
            n = o(t) ? Array.prototype.forEach || function(t) {
                for (var e = 0, n = this.length; n > e; e++) t(this[e], e, this)
            } : function(t) {
                for (var e in this) this.hasOwnProperty(e) && t(this[e], e, this)
            }, n.apply(t, [e])
        }, t.prototype.getScoreFunction = function(t, e) {
            var n, r, i, o;
            n = this, t = n.prepareSearch(t, e), i = t.tokens, r = t.options.fields, o = i.length;
            var a = function(t, e) {
                    var n, r;
                    return t ? (t = String(t || ""), r = t.search(e.regex), -1 === r ? 0 : (n = e.string.length / t.length, 0 === r && (n += .5), n)) : 0
                },
                s = function() {
                    var t = r.length;
                    return t ? 1 === t ? function(t, e) {
                        return a(e[r[0]], t)
                    } : function(e, n) {
                        for (var i = 0, o = 0; t > i; i++) o += a(n[r[i]], e);
                        return o / t
                    } : function() {
                        return 0
                    }
                }();
            return o ? 1 === o ? function(t) {
                return s(i[0], t)
            } : "and" === t.options.conjunction ? function(t) {
                for (var e, n = 0, r = 0; o > n; n++) {
                    if (e = s(i[n], t), 0 >= e) return 0;
                    r += e
                }
                return r / o
            } : function(t) {
                for (var e = 0, n = 0; o > e; e++) n += s(i[e], t);
                return n / o
            } : function() {
                return 0
            }
        }, t.prototype.getSortFunction = function(t, n) {
            var r, i, o, a, s, u, l, c, f, d, p;
            if (o = this, t = o.prepareSearch(t, n), p = !t.query && n.sort_empty || n.sort, f = function(t, e) {
                    return "$score" === t ? e.score : o.items[e.id][t]
                }, s = [], p)
                for (r = 0, i = p.length; i > r; r++)(t.query || "$score" !== p[r].field) && s.push(p[r]);
            if (t.query) {
                for (d = !0, r = 0, i = s.length; i > r; r++)
                    if ("$score" === s[r].field) {
                        d = !1;
                        break
                    }
                d && s.unshift({
                    field: "$score",
                    direction: "desc"
                })
            } else
                for (r = 0, i = s.length; i > r; r++)
                    if ("$score" === s[r].field) {
                        s.splice(r, 1);
                        break
                    } for (c = [], r = 0, i = s.length; i > r; r++) c.push("desc" === s[r].direction ? -1 : 1);
            return u = s.length, u ? 1 === u ? (a = s[0].field, l = c[0], function(t, n) {
                return l * e(f(a, t), f(a, n))
            }) : function(t, n) {
                var r, i, o;
                for (r = 0; u > r; r++)
                    if (o = s[r].field, i = c[r] * e(f(o, t), f(o, n))) return i;
                return 0
            } : null
        }, t.prototype.prepareSearch = function(t, e) {
            if ("object" == typeof t) return t;
            e = n({}, e);
            var r = e.fields,
                i = e.sort,
                a = e.sort_empty;
            return r && !o(r) && (e.fields = [r]), i && !o(i) && (e.sort = [i]), a && !o(a) && (e.sort_empty = [a]), {
                options: e,
                query: String(t || "").toLowerCase(),
                tokens: this.tokenize(t),
                total: 0,
                items: []
            }
        }, t.prototype.search = function(t, e) {
            var n, r, i, o, a = this;
            return r = this.prepareSearch(t, e), e = r.options, t = r.query, o = e.score || a.getScoreFunction(r), t.length ? a.iterator(a.items, function(t, i) {
                n = o(t), (e.filter === !1 || n > 0) && r.items.push({
                    score: n,
                    id: i
                })
            }) : a.iterator(a.items, function(t, e) {
                r.items.push({
                    score: 1,
                    id: e
                })
            }), i = a.getSortFunction(r, e), i && r.items.sort(i), r.total = r.items.length, "number" == typeof e.limit && (r.items = r.items.slice(0, e.limit)), r
        };
        var e = function(t, e) {
                return "number" == typeof t && "number" == typeof e ? t > e ? 1 : e > t ? -1 : 0 : (t = s(String(t || "")), e = s(String(e || "")), t > e ? 1 : e > t ? -1 : 0)
            },
            n = function(t) {
                var e, n, r, i;
                for (e = 1, n = arguments.length; n > e; e++)
                    if (i = arguments[e])
                        for (r in i) i.hasOwnProperty(r) && (t[r] = i[r]);
                return t
            },
            r = function(t) {
                return (t + "").replace(/^\s+|\s+$|/g, "")
            },
            i = function(t) {
                return (t + "").replace(/([.?*+^$[\]\\(){}|-])/g, "\\$1")
            },
            o = Array.isArray || $ && $.isArray || function(t) {
                return "[object Array]" === Object.prototype.toString.call(t)
            },
            a = {
                a: "[a\xc0\xc1\xc2\xc3\xc4\xc5\xe0\xe1\xe2\xe3\xe4\xe5\u0100\u0101\u0105\u0104]",
                c: "[c\xc7\xe7\u0107\u0106\u010d\u010c]",
                d: "[d\u0111\u0110\u010f\u010e]",
                e: "[e\xc8\xc9\xca\xcb\xe8\xe9\xea\xeb\u011b\u011a\u0112\u0113\u0119\u0118]",
                i: "[i\xcc\xcd\xce\xcf\xec\xed\xee\xef\u012a\u012b]",
                l: "[l\u0142\u0141]",
                n: "[n\xd1\xf1\u0148\u0147\u0144\u0143]",
                o: "[o\xd2\xd3\xd4\xd5\xd5\xd6\xd8\xf2\xf3\xf4\xf5\xf6\xf8\u014c\u014d]",
                r: "[r\u0159\u0158]",
                s: "[s\u0160\u0161\u015b\u015a]",
                t: "[t\u0165\u0164]",
                u: "[u\xd9\xda\xdb\xdc\xf9\xfa\xfb\xfc\u016f\u016e\u016a\u016b]",
                y: "[y\u0178\xff\xfd\xdd]",
                z: "[z\u017d\u017e\u017c\u017b\u017a\u0179]"
            },
            s = function() {
                var t, e, n, r, i = "",
                    o = {};
                for (n in a)
                    if (a.hasOwnProperty(n))
                        for (r = a[n].substring(2, a[n].length - 1), i += r, t = 0, e = r.length; e > t; t++) o[r.charAt(t)] = n;
                var s = new RegExp("[" + i + "]", "g");
                return function(t) {
                    return t.replace(s, function(t) {
                        return o[t]
                    }).toLowerCase()
                }
            }();
        return t
    }), function(t, e) {
        "function" == typeof define && define.amd ? define("microplugin", e) : "object" == typeof exports ? module.exports = e() : t.MicroPlugin = e()
    }(this, function() {
        var t = {};
        t.mixin = function(t) {
            t.plugins = {}, t.prototype.initializePlugins = function(t) {
                var n, r, i, o = this,
                    a = [];
                if (o.plugins = {
                        names: [],
                        settings: {},
                        requested: {},
                        loaded: {}
                    }, e.isArray(t))
                    for (n = 0, r = t.length; r > n; n++) "string" == typeof t[n] ? a.push(t[n]) : (o.plugins.settings[t[n].name] = t[n].options, a.push(t[n].name));
                else if (t)
                    for (i in t) t.hasOwnProperty(i) && (o.plugins.settings[i] = t[i], a.push(i));
                for (; a.length;) o.require(a.shift())
            }, t.prototype.loadPlugin = function(e) {
                var n = this,
                    r = n.plugins,
                    i = t.plugins[e];
                if (!t.plugins.hasOwnProperty(e)) throw new Error('Unable to find "' + e + '" plugin');
                r.requested[e] = !0, r.loaded[e] = i.fn.apply(n, [n.plugins.settings[e] || {}]), r.names.push(e)
            }, t.prototype.require = function(t) {
                var e = this,
                    n = e.plugins;
                if (!e.plugins.loaded.hasOwnProperty(t)) {
                    if (n.requested[t]) throw new Error('Plugin has circular dependency ("' + t + '")');
                    e.loadPlugin(t)
                }
                return n.loaded[t]
            }, t.define = function(e, n) {
                t.plugins[e] = {
                    name: e,
                    fn: n
                }
            }
        };
        var e = {
            isArray: Array.isArray || function(t) {
                return "[object Array]" === Object.prototype.toString.call(t)
            }
        };
        return t
    }), function(t, e) {
        "function" == typeof define && define.amd ? define("selectize", ["jquery", "sifter", "microplugin"], e) : "object" == typeof exports ? module.exports = e(require("jquery"), require("sifter"), require("microplugin")) : t.Selectize = e(t.jQuery, t.Sifter, t.MicroPlugin)
    }(this, function(t, e, n) {
        "use strict";
        var r = function(t, e) {
                if ("string" != typeof e || e.length) {
                    var n = "string" == typeof e ? new RegExp(e, "i") : e,
                        r = function(t) {
                            var e = 0;
                            if (3 === t.nodeType) {
                                var i = t.data.search(n);
                                if (i >= 0 && t.data.length > 0) {
                                    var o = t.data.match(n),
                                        a = document.createElement("span");
                                    a.className = "highlight";
                                    var s = t.splitText(i),
                                        u = (s.splitText(o[0].length), s.cloneNode(!0));
                                    a.appendChild(u), s.parentNode.replaceChild(a, s), e = 1
                                }
                            } else if (1 === t.nodeType && t.childNodes && !/(script|style)/i.test(t.tagName))
                                for (var l = 0; l < t.childNodes.length; ++l) l += r(t.childNodes[l]);
                            return e
                        };
                    return t.each(function() {
                        r(this)
                    })
                }
            },
            i = function() {};
        i.prototype = {
            on: function(t, e) {
                this._events = this._events || {}, this._events[t] = this._events[t] || [], this._events[t].push(e)
            },
            off: function(t, e) {
                var n = arguments.length;
                return 0 === n ? delete this._events : 1 === n ? delete this._events[t] : (this._events = this._events || {}, void(t in this._events != !1 && this._events[t].splice(this._events[t].indexOf(e), 1)))
            },
            trigger: function(t) {
                if (this._events = this._events || {}, t in this._events != !1)
                    for (var e = 0; e < this._events[t].length; e++) this._events[t][e].apply(this, Array.prototype.slice.call(arguments, 1))
            }
        }, i.mixin = function(t) {
            for (var e = ["on", "off", "trigger"], n = 0; n < e.length; n++) t.prototype[e[n]] = i.prototype[e[n]]
        };
        var o = /Mac/.test(navigator.userAgent),
            a = 65,
            s = 13,
            u = 27,
            l = 37,
            c = 38,
            f = 80,
            d = 39,
            p = 40,
            h = 78,
            g = 8,
            m = 46,
            v = 16,
            y = o ? 91 : 17,
            b = o ? 18 : 17,
            w = 9,
            x = 1,
            _ = 2,
            C = !/android/i.test(window.navigator.userAgent) && !!document.createElement("form").validity,
            k = function(t) {
                return "undefined" != typeof t
            },
            T = function(t) {
                return "undefined" == typeof t || null === t ? null : "boolean" == typeof t ? t ? "1" : "0" : t + ""
            },
            S = function(t) {
                return (t + "").replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;")
            },
            j = function(t) {
                return (t + "").replace(/\$/g, "$$$$")
            },
            E = {};
        E.before = function(t, e, n) {
            var r = t[e];
            t[e] = function() {
                return n.apply(t, arguments), r.apply(t, arguments)
            }
        }, E.after = function(t, e, n) {
            var r = t[e];
            t[e] = function() {
                var e = r.apply(t, arguments);
                return n.apply(t, arguments), e
            }
        };
        var N = function(t) {
                var e = !1;
                return function() {
                    e || (e = !0, t.apply(this, arguments))
                }
            },
            A = function(t, e) {
                var n;
                return function() {
                    var r = this,
                        i = arguments;
                    window.clearTimeout(n), n = window.setTimeout(function() {
                        t.apply(r, i)
                    }, e)
                }
            },
            $ = function(t, e, n) {
                var r, i = t.trigger,
                    o = {};
                t.trigger = function() {
                    var n = arguments[0];
                    return -1 === e.indexOf(n) ? i.apply(t, arguments) : void(o[n] = arguments)
                }, n.apply(t, []), t.trigger = i;
                for (r in o) o.hasOwnProperty(r) && i.apply(t, o[r])
            },
            O = function(t, e, n, r) {
                t.on(e, n, function(e) {
                    for (var n = e.target; n && n.parentNode !== t[0];) n = n.parentNode;
                    return e.currentTarget = n, r.apply(this, [e])
                })
            },
            D = function(t) {
                var e = {};
                if ("selectionStart" in t) e.start = t.selectionStart, e.length = t.selectionEnd - e.start;
                else if (document.selection) {
                    t.focus();
                    var n = document.selection.createRange(),
                        r = document.selection.createRange().text.length;
                    n.moveStart("character", -t.value.length), e.start = n.text.length - r, e.length = r
                }
                return e
            },
            I = function(t, e, n) {
                var r, i, o = {};
                if (n)
                    for (r = 0, i = n.length; i > r; r++) o[n[r]] = t.css(n[r]);
                else o = t.css();
                e.css(o)
            },
            L = function(e, n) {
                if (!e) return 0;
                var r = t("<test>").css({
                    position: "absolute",
                    top: -99999,
                    left: -99999,
                    width: "auto",
                    padding: 0,
                    whiteSpace: "pre"
                }).text(e).appendTo("body");
                I(n, r, ["letterSpacing", "fontSize", "fontFamily", "fontWeight", "textTransform"]);
                var i = r.width();
                return r.remove(), i
            },
            F = function(t) {
                var e = null,
                    n = function(n, r) {
                        var i, o, a, s, u, l, c, f;
                        n = n || window.event || {}, r = r || {}, n.metaKey || n.altKey || (r.force || t.data("grow") !== !1) && (i = t.val(), n.type && "keydown" === n.type.toLowerCase() && (o = n.keyCode, a = o >= 97 && 122 >= o || o >= 65 && 90 >= o || o >= 48 && 57 >= o || 32 === o, o === m || o === g ? (f = D(t[0]), f.length ? i = i.substring(0, f.start) + i.substring(f.start + f.length) : o === g && f.start ? i = i.substring(0, f.start - 1) + i.substring(f.start + 1) : o === m && "undefined" != typeof f.start && (i = i.substring(0, f.start) + i.substring(f.start + 1))) : a && (l = n.shiftKey, c = String.fromCharCode(n.keyCode), c = l ? c.toUpperCase() : c.toLowerCase(), i += c)), s = t.attr("placeholder"), !i && s && (i = s), u = L(i, t) + 4, u !== e && (e = u, t.width(u), t.triggerHandler("resize")))
                    };
                t.on("keydown keyup update blur", n), n()
            },
            R = function(n, r) {
                var i, o, a, s, u = this;
                s = n[0], s.selectize = u;
                var l = window.getComputedStyle && window.getComputedStyle(s, null);
                if (a = l ? l.getPropertyValue("direction") : s.currentStyle && s.currentStyle.direction, a = a || n.parents("[dir]:first").attr("dir") || "", t.extend(u, {
                        order: 0,
                        settings: r,
                        $input: n,
                        tabIndex: n.attr("tabindex") || "",
                        tagType: "select" === s.tagName.toLowerCase() ? x : _,
                        rtl: /rtl/i.test(a),
                        eventNS: ".selectize" + ++R.count,
                        highlightedValue: null,
                        isOpen: !1,
                        isDisabled: !1,
                        isRequired: n.is("[required]"),
                        isInvalid: !1,
                        isLocked: !1,
                        isFocused: !1,
                        isInputHidden: !1,
                        isSetup: !1,
                        isShiftDown: !1,
                        isCmdDown: !1,
                        isCtrlDown: !1,
                        ignoreFocus: !1,
                        ignoreBlur: !1,
                        ignoreHover: !1,
                        hasOptions: !1,
                        currentResults: null,
                        lastValue: "",
                        caretPos: 0,
                        loading: 0,
                        loadedSearches: {},
                        $activeOption: null,
                        $activeItems: [],
                        optgroups: {},
                        options: {},
                        userOptions: {},
                        items: [],
                        renderCache: {},
                        onSearchChange: null === r.loadThrottle ? u.onSearchChange : A(u.onSearchChange, r.loadThrottle)
                    }), u.sifter = new e(this.options, {
                        diacritics: r.diacritics
                    }), u.settings.options) {
                    for (i = 0, o = u.settings.options.length; o > i; i++) u.registerOption(u.settings.options[i]);
                    delete u.settings.options
                }
                if (u.settings.optgroups) {
                    for (i = 0, o = u.settings.optgroups.length; o > i; i++) u.registerOptionGroup(u.settings.optgroups[i]);
                    delete u.settings.optgroups
                }
                u.settings.mode = u.settings.mode || (1 === u.settings.maxItems ? "single" : "multi"), "boolean" != typeof u.settings.hideSelected && (u.settings.hideSelected = "multi" === u.settings.mode), u.initializePlugins(u.settings.plugins), u.setupCallbacks(), u.setupTemplates(), u.setup()
            };
        return i.mixin(R), n.mixin(R), t.extend(R.prototype, {
            setup: function() {
                var e, n, r, i, a, s, u, l, c, f = this,
                    d = f.settings,
                    p = f.eventNS,
                    h = t(window),
                    g = t(document),
                    m = f.$input;
                if (u = f.settings.mode, l = m.attr("class") || "", e = t("<div>").addClass(d.wrapperClass).addClass(l).addClass(u), n = t("<div>").addClass(d.inputClass).addClass("items").appendTo(e), r = t('<input type="text" autocomplete="off" />').appendTo(n).attr("tabindex", m.is(":disabled") ? "-1" : f.tabIndex), s = t(d.dropdownParent || e), i = t("<div>").addClass(d.dropdownClass).addClass(u).hide().appendTo(s), a = t("<div>").addClass(d.dropdownContentClass).appendTo(i), f.settings.copyClassesToDropdown && i.addClass(l), e.css({
                        width: m[0].style.width
                    }), f.plugins.names.length && (c = "plugin-" + f.plugins.names.join(" plugin-"), e.addClass(c), i.addClass(c)), (null === d.maxItems || d.maxItems > 1) && f.tagType === x && m.attr("multiple", "multiple"), f.settings.placeholder && r.attr("placeholder", d.placeholder), !f.settings.splitOn && f.settings.delimiter) {
                    var w = f.settings.delimiter.replace(/[-\/\\^$*+?.()|[\]{}]/g, "\\$&");
                    f.settings.splitOn = new RegExp("\\s*" + w + "+\\s*")
                }
                m.attr("autocorrect") && r.attr("autocorrect", m.attr("autocorrect")), m.attr("autocapitalize") && r.attr("autocapitalize", m.attr("autocapitalize")), f.$wrapper = e, f.$control = n, f.$control_input = r, f.$dropdown = i, f.$dropdown_content = a, i.on("mouseenter", "[data-selectable]", function() {
                    return f.onOptionHover.apply(f, arguments)
                }), i.on("mousedown click", "[data-selectable]", function() {
                    return f.onOptionSelect.apply(f, arguments)
                }), O(n, "mousedown", "*:not(input)", function() {
                    return f.onItemSelect.apply(f, arguments)
                }), F(r), n.on({
                    mousedown: function() {
                        return f.onMouseDown.apply(f, arguments)
                    },
                    click: function() {
                        return f.onClick.apply(f, arguments)
                    }
                }), r.on({
                    mousedown: function(t) {
                        t.stopPropagation()
                    },
                    keydown: function() {
                        return f.onKeyDown.apply(f, arguments)
                    },
                    keyup: function() {
                        return f.onKeyUp.apply(f, arguments)
                    },
                    keypress: function() {
                        return f.onKeyPress.apply(f, arguments)
                    },
                    resize: function() {
                        f.positionDropdown.apply(f, [])
                    },
                    blur: function() {
                        return f.onBlur.apply(f, arguments)
                    },
                    focus: function() {
                        return f.ignoreBlur = !1, f.onFocus.apply(f, arguments)
                    },
                    paste: function() {
                        return f.onPaste.apply(f, arguments)
                    }
                }), g.on("keydown" + p, function(t) {
                    f.isCmdDown = t[o ? "metaKey" : "ctrlKey"], f.isCtrlDown = t[o ? "altKey" : "ctrlKey"], f.isShiftDown = t.shiftKey
                }), g.on("keyup" + p, function(t) {
                    t.keyCode === b && (f.isCtrlDown = !1), t.keyCode === v && (f.isShiftDown = !1), t.keyCode === y && (f.isCmdDown = !1)
                }), g.on("mousedown" + p, function(t) {
                    if (f.isFocused) {
                        if (t.target === f.$dropdown[0] || t.target.parentNode === f.$dropdown[0]) return !1;
                        f.$control.has(t.target).length || t.target === f.$control[0] || f.blur(t.target)
                    }
                }), h.on(["scroll" + p, "resize" + p].join(" "), function() {
                    f.isOpen && f.positionDropdown.apply(f, arguments)
                }), h.on("mousemove" + p, function() {
                    f.ignoreHover = !1
                }), this.revertSettings = {
                    $children: m.children().detach(),
                    tabindex: m.attr("tabindex")
                }, m.attr("tabindex", -1).hide().after(f.$wrapper), t.isArray(d.items) && (f.setValue(d.items), delete d.items), C && m.on("invalid" + p, function(t) {
                    t.preventDefault(), f.isInvalid = !0, f.refreshState()
                }), f.updateOriginalInput(), f.refreshItems(), f.refreshState(), f.updatePlaceholder(), f.isSetup = !0, m.is(":disabled") && f.disable(), f.on("change", this.onChange), m.data("selectize", f), m.addClass("selectized"), f.trigger("initialize"), d.preload === !0 && f.onSearchChange("")
            },
            setupTemplates: function() {
                var e = this,
                    n = e.settings.labelField,
                    r = e.settings.optgroupLabelField,
                    i = {
                        optgroup: function(t) {
                            return '<div class="optgroup">' + t.html + "</div>"
                        },
                        optgroup_header: function(t, e) {
                            return '<div class="optgroup-header">' + e(t[r]) + "</div>"
                        },
                        option: function(t, e) {
                            return '<div class="option">' + e(t[n]) + "</div>"
                        },
                        item: function(t, e) {
                            return '<div class="item">' + e(t[n]) + "</div>"
                        },
                        option_create: function(t, e) {
                            return '<div class="create">Add <strong>' + e(t.input) + "</strong>&hellip;</div>"
                        }
                    };
                e.settings.render = t.extend({}, i, e.settings.render)
            },
            setupCallbacks: function() {
                var t, e, n = {
                    initialize: "onInitialize",
                    change: "onChange",
                    item_add: "onItemAdd",
                    item_remove: "onItemRemove",
                    clear: "onClear",
                    option_add: "onOptionAdd",
                    option_remove: "onOptionRemove",
                    option_clear: "onOptionClear",
                    optgroup_add: "onOptionGroupAdd",
                    optgroup_remove: "onOptionGroupRemove",
                    optgroup_clear: "onOptionGroupClear",
                    dropdown_open: "onDropdownOpen",
                    dropdown_close: "onDropdownClose",
                    type: "onType",
                    load: "onLoad",
                    focus: "onFocus",
                    blur: "onBlur"
                };
                for (t in n) n.hasOwnProperty(t) && (e = this.settings[n[t]], e && this.on(t, e))
            },
            onClick: function(t) {
                var e = this;
                e.isFocused || (e.focus(), t.preventDefault())
            },
            onMouseDown: function(e) {
                {
                    var n = this,
                        r = e.isDefaultPrevented();
                    t(e.target)
                }
                if (n.isFocused) {
                    if (e.target !== n.$control_input[0]) return "single" === n.settings.mode ? n.isOpen ? n.close() : n.open() : r || n.setActiveItem(null), !1
                } else r || window.setTimeout(function() {
                    n.focus()
                }, 0)
            },
            onChange: function() {
                this.$input.trigger("change")
            },
            onPaste: function(e) {
                var n = this;
                n.isFull() || n.isInputHidden || n.isLocked ? e.preventDefault() : n.settings.splitOn && setTimeout(function() {
                    for (var e = t.trim(n.$control_input.val() || "").split(n.settings.splitOn), r = 0, i = e.length; i > r; r++) n.createItem(e[r])
                }, 0)
            },
            onKeyPress: function(t) {
                if (this.isLocked) return t && t.preventDefault();
                var e = String.fromCharCode(t.keyCode || t.which);
                return this.settings.create && "multi" === this.settings.mode && e === this.settings.delimiter ? (this.createItem(), t.preventDefault(), !1) : void 0
            },
            onKeyDown: function(t) {
                var e = (t.target === this.$control_input[0], this);
                if (e.isLocked) return void(t.keyCode !== w && t.preventDefault());
                switch (t.keyCode) {
                    case a:
                        if (e.isCmdDown) return void e.selectAll();
                        break;
                    case u:
                        return void(e.isOpen && (t.preventDefault(), t.stopPropagation(), e.close()));
                    case h:
                        if (!t.ctrlKey || t.altKey) break;
                    case p:
                        if (!e.isOpen && e.hasOptions) e.open();
                        else if (e.$activeOption) {
                            e.ignoreHover = !0;
                            var n = e.getAdjacentOption(e.$activeOption, 1);
                            n.length && e.setActiveOption(n, !0, !0)
                        }
                        return void t.preventDefault();
                    case f:
                        if (!t.ctrlKey || t.altKey) break;
                    case c:
                        if (e.$activeOption) {
                            e.ignoreHover = !0;
                            var r = e.getAdjacentOption(e.$activeOption, -1);
                            r.length && e.setActiveOption(r, !0, !0)
                        }
                        return void t.preventDefault();
                    case s:
                        return void(e.isOpen && e.$activeOption && (e.onOptionSelect({
                            currentTarget: e.$activeOption
                        }), t.preventDefault()));
                    case l:
                        return void e.advanceSelection(-1, t);
                    case d:
                        return void e.advanceSelection(1, t);
                    case w:
                        return e.settings.selectOnTab && e.isOpen && e.$activeOption && (e.onOptionSelect({
                            currentTarget: e.$activeOption
                        }), e.isFull() || t.preventDefault()), void(e.settings.create && e.createItem() && t.preventDefault());
                    case g:
                    case m:
                        return void e.deleteSelection(t)
                }
                return !e.isFull() && !e.isInputHidden || (o ? t.metaKey : t.ctrlKey) ? void 0 : void t.preventDefault()
            },
            onKeyUp: function(t) {
                var e = this;
                if (e.isLocked) return t && t.preventDefault();
                var n = e.$control_input.val() || "";
                e.lastValue !== n && (e.lastValue = n, e.onSearchChange(n), e.refreshOptions(), e.trigger("type", n))
            },
            onSearchChange: function(t) {
                var e = this,
                    n = e.settings.load;
                n && (e.loadedSearches.hasOwnProperty(t) || (e.loadedSearches[t] = !0, e.load(function(r) {
                    n.apply(e, [t, r])
                })))
            },
            onFocus: function(t) {
                var e = this,
                    n = e.isFocused;
                return e.isDisabled ? (e.blur(), t && t.preventDefault(), !1) : void(e.ignoreFocus || (e.isFocused = !0, "focus" === e.settings.preload && e.onSearchChange(""), n || e.trigger("focus"), e.$activeItems.length || (e.showInput(), e.setActiveItem(null), e.refreshOptions(!!e.settings.openOnFocus)), e.refreshState()))
            },
            onBlur: function(t, e) {
                var n = this;
                if (n.isFocused && (n.isFocused = !1, !n.ignoreFocus)) {
                    if (!n.ignoreBlur && document.activeElement === n.$dropdown_content[0]) return n.ignoreBlur = !0, void n.onFocus(t);
                    var r = function() {
                        n.close(), n.setTextboxValue(""), n.setActiveItem(null), n.setActiveOption(null), n.setCaret(n.items.length), n.refreshState(), (e || document.body).focus(), n.ignoreFocus = !1, n.trigger("blur")
                    };
                    n.ignoreFocus = !0, n.settings.create && n.settings.createOnBlur ? n.createItem(null, !1, r) : r()
                }
            },
            onOptionHover: function(t) {
                this.ignoreHover || this.setActiveOption(t.currentTarget, !1)
            },
            onOptionSelect: function(e) {
                var n, r, i = this;
                e.preventDefault && (e.preventDefault(), e.stopPropagation()), r = t(e.currentTarget), r.hasClass("create") ? i.createItem(null, function() {
                    i.settings.closeAfterSelect && i.close()
                }) : (n = r.attr("data-value"), "undefined" != typeof n && (i.lastQuery = null, i.setTextboxValue(""), i.addItem(n), i.settings.closeAfterSelect ? i.close() : !i.settings.hideSelected && e.type && /mouse/.test(e.type) && i.setActiveOption(i.getOption(n))))
            },
            onItemSelect: function(t) {
                var e = this;
                e.isLocked || "multi" === e.settings.mode && (t.preventDefault(), e.setActiveItem(t.currentTarget, t))
            },
            load: function(t) {
                var e = this,
                    n = e.$wrapper.addClass(e.settings.loadingClass);
                e.loading++, t.apply(e, [function(t) {
                    e.loading = Math.max(e.loading - 1, 0), t && t.length && (e.addOption(t), e.refreshOptions(e.isFocused && !e.isInputHidden)), e.loading || n.removeClass(e.settings.loadingClass), e.trigger("load", t)
                }])
            },
            setTextboxValue: function(t) {
                var e = this.$control_input,
                    n = e.val() !== t;
                n && (e.val(t).triggerHandler("update"), this.lastValue = t)
            },
            getValue: function() {
                return this.tagType === x && this.$input.attr("multiple") ? this.items : this.items.join(this.settings.delimiter)
            },
            setValue: function(t, e) {
                var n = e ? [] : ["change"];
                $(this, n, function() {
                    this.clear(), this.addItems(t, e)
                })
            },
            setActiveItem: function(e, n) {
                var r, i, o, a, s, u, l, c, f = this;
                if ("single" !== f.settings.mode) {
                    if (e = t(e), !e.length) return t(f.$activeItems).removeClass("active"), f.$activeItems = [], void(f.isFocused && f.showInput());
                    if (r = n && n.type.toLowerCase(), "mousedown" === r && f.isShiftDown && f.$activeItems.length) {
                        for (c = f.$control.children(".active:last"), a = Array.prototype.indexOf.apply(f.$control[0].childNodes, [c[0]]), s = Array.prototype.indexOf.apply(f.$control[0].childNodes, [e[0]]), a > s && (l = a, a = s, s = l), i = a; s >= i; i++) u = f.$control[0].childNodes[i], -1 === f.$activeItems.indexOf(u) && (t(u).addClass("active"), f.$activeItems.push(u));
                        n.preventDefault()
                    } else "mousedown" === r && f.isCtrlDown || "keydown" === r && this.isShiftDown ? e.hasClass("active") ? (o = f.$activeItems.indexOf(e[0]), f.$activeItems.splice(o, 1), e.removeClass("active")) : f.$activeItems.push(e.addClass("active")[0]) : (t(f.$activeItems).removeClass("active"), f.$activeItems = [e.addClass("active")[0]]);
                    f.hideInput(), this.isFocused || f.focus()
                }
            },
            setActiveOption: function(e, n, r) {
                var i, o, a, s, u, l = this;
                l.$activeOption && l.$activeOption.removeClass("active"), l.$activeOption = null, e = t(e), e.length && (l.$activeOption = e.addClass("active"), (n || !k(n)) && (i = l.$dropdown_content.height(), o = l.$activeOption.outerHeight(!0), n = l.$dropdown_content.scrollTop() || 0, a = l.$activeOption.offset().top - l.$dropdown_content.offset().top + n, s = a, u = a - i + o, a + o > i + n ? l.$dropdown_content.stop().animate({
                    scrollTop: u
                }, r ? l.settings.scrollDuration : 0) : n > a && l.$dropdown_content.stop().animate({
                    scrollTop: s
                }, r ? l.settings.scrollDuration : 0)))
            },
            selectAll: function() {
                var t = this;
                "single" !== t.settings.mode && (t.$activeItems = Array.prototype.slice.apply(t.$control.children(":not(input)").addClass("active")), t.$activeItems.length && (t.hideInput(), t.close()), t.focus())
            },
            hideInput: function() {
                var t = this;
                t.setTextboxValue(""), t.$control_input.css({
                    opacity: 0,
                    position: "absolute",
                    left: t.rtl ? 1e4 : -1e4
                }), t.isInputHidden = !0
            },
            showInput: function() {
                this.$control_input.css({
                    opacity: 1,
                    position: "relative",
                    left: 0
                }), this.isInputHidden = !1
            },
            focus: function() {
                var t = this;
                t.isDisabled || (t.ignoreFocus = !0, t.$control_input[0].focus(), window.setTimeout(function() {
                    t.ignoreFocus = !1, t.onFocus()
                }, 0))
            },
            blur: function(t) {
                this.$control_input[0].blur(), this.onBlur(null, t)
            },
            getScoreFunction: function(t) {
                return this.sifter.getScoreFunction(t, this.getSearchOptions())
            },
            getSearchOptions: function() {
                var t = this.settings,
                    e = t.sortField;
                return "string" == typeof e && (e = [{
                    field: e
                }]), {
                    fields: t.searchField,
                    conjunction: t.searchConjunction,
                    sort: e
                }
            },
            search: function(e) {
                var n, r, i, o = this,
                    a = o.settings,
                    s = this.getSearchOptions();
                if (a.score && (i = o.settings.score.apply(this, [e]), "function" != typeof i)) throw new Error('Selectize "score" setting must be a function that returns a function');
                if (e !== o.lastQuery ? (o.lastQuery = e, r = o.sifter.search(e, t.extend(s, {
                        score: i
                    })), o.currentResults = r) : r = t.extend(!0, {}, o.currentResults), a.hideSelected)
                    for (n = r.items.length - 1; n >= 0; n--) - 1 !== o.items.indexOf(T(r.items[n].id)) && r.items.splice(n, 1);
                return r
            },
            refreshOptions: function(e) {
                var n, i, o, a, s, u, l, c, f, d, p, h, g, m, v, y;
                "undefined" == typeof e && (e = !0);
                var b = this,
                    w = t.trim(b.$control_input.val()),
                    x = b.search(w),
                    _ = b.$dropdown_content,
                    C = b.$activeOption && T(b.$activeOption.attr("data-value"));
                for (a = x.items.length, "number" == typeof b.settings.maxOptions && (a = Math.min(a, b.settings.maxOptions)), s = {}, u = [], n = 0; a > n; n++)
                    for (l = b.options[x.items[n].id], c = b.render("option", l), f = l[b.settings.optgroupField] || "", d = t.isArray(f) ? f : [f], i = 0, o = d && d.length; o > i; i++) f = d[i], b.optgroups.hasOwnProperty(f) || (f = ""), s.hasOwnProperty(f) || (s[f] = [], u.push(f)), s[f].push(c);
                for (this.settings.lockOptgroupOrder && u.sort(function(t, e) {
                        var n = b.optgroups[t].$order || 0,
                            r = b.optgroups[e].$order || 0;
                        return n - r
                    }), p = [], n = 0, a = u.length; a > n; n++) f = u[n], b.optgroups.hasOwnProperty(f) && s[f].length ? (h = b.render("optgroup_header", b.optgroups[f]) || "", h += s[f].join(""), p.push(b.render("optgroup", t.extend({}, b.optgroups[f], {
                    html: h
                })))) : p.push(s[f].join(""));
                if (_.html(p.join("")), b.settings.highlight && x.query.length && x.tokens.length)
                    for (n = 0, a = x.tokens.length; a > n; n++) r(_, x.tokens[n].regex);
                if (!b.settings.hideSelected)
                    for (n = 0, a = b.items.length; a > n; n++) b.getOption(b.items[n]).addClass("selected");
                g = b.canCreate(w), g && (_.prepend(b.render("option_create", {
                    input: w
                })), y = t(_[0].childNodes[0])), b.hasOptions = x.items.length > 0 || g, b.hasOptions ? (x.items.length > 0 ? (v = C && b.getOption(C), v && v.length ? m = v : "single" === b.settings.mode && b.items.length && (m = b.getOption(b.items[0])), m && m.length || (m = y && !b.settings.addPrecedence ? b.getAdjacentOption(y, 1) : _.find("[data-selectable]:first"))) : m = y, b.setActiveOption(m), e && !b.isOpen && b.open()) : (b.setActiveOption(null), e && b.isOpen && b.close())
            },
            addOption: function(e) {
                var n, r, i, o = this;
                if (t.isArray(e))
                    for (n = 0, r = e.length; r > n; n++) o.addOption(e[n]);
                else(i = o.registerOption(e)) && (o.userOptions[i] = !0, o.lastQuery = null, o.trigger("option_add", i, e))
            },
            registerOption: function(t) {
                var e = T(t[this.settings.valueField]);
                return !e || this.options.hasOwnProperty(e) ? !1 : (t.$order = t.$order || ++this.order, this.options[e] = t, e)
            },
            registerOptionGroup: function(t) {
                var e = T(t[this.settings.optgroupValueField]);
                return e ? (t.$order = t.$order || ++this.order, this.optgroups[e] = t, e) : !1
            },
            addOptionGroup: function(t, e) {
                e[this.settings.optgroupValueField] = t, (t = this.registerOptionGroup(e)) && this.trigger("optgroup_add", t, e)
            },
            removeOptionGroup: function(t) {
                this.optgroups.hasOwnProperty(t) && (delete this.optgroups[t], this.renderCache = {}, this.trigger("optgroup_remove", t))
            },
            clearOptionGroups: function() {
                this.optgroups = {}, this.renderCache = {}, this.trigger("optgroup_clear")
            },
            updateOption: function(e, n) {
                var r, i, o, a, s, u, l, c = this;
                if (e = T(e), o = T(n[c.settings.valueField]), null !== e && c.options.hasOwnProperty(e)) {
                    if ("string" != typeof o) throw new Error("Value must be set in option data");
                    l = c.options[e].$order, o !== e && (delete c.options[e], a = c.items.indexOf(e), -1 !== a && c.items.splice(a, 1, o)), n.$order = n.$order || l, c.options[o] = n, s = c.renderCache.item, u = c.renderCache.option, s && (delete s[e], delete s[o]), u && (delete u[e], delete u[o]), -1 !== c.items.indexOf(o) && (r = c.getItem(e), i = t(c.render("item", n)), r.hasClass("active") && i.addClass("active"), r.replaceWith(i)), c.lastQuery = null, c.isOpen && c.refreshOptions(!1)
                }
            },
            removeOption: function(t, e) {
                var n = this;
                t = T(t);
                var r = n.renderCache.item,
                    i = n.renderCache.option;
                r && delete r[t], i && delete i[t], delete n.userOptions[t], delete n.options[t], n.lastQuery = null, n.trigger("option_remove", t), n.removeItem(t, e)
            },
            clearOptions: function() {
                var t = this;
                t.loadedSearches = {}, t.userOptions = {}, t.renderCache = {}, t.options = t.sifter.items = {}, t.lastQuery = null, t.trigger("option_clear"), t.clear()
            },
            getOption: function(t) {
                return this.getElementWithValue(t, this.$dropdown_content.find("[data-selectable]"))
            },
            getAdjacentOption: function(e, n) {
                var r = this.$dropdown.find("[data-selectable]"),
                    i = r.index(e) + n;
                return i >= 0 && i < r.length ? r.eq(i) : t()
            },
            getElementWithValue: function(e, n) {
                if (e = T(e), "undefined" != typeof e && null !== e)
                    for (var r = 0, i = n.length; i > r; r++)
                        if (n[r].getAttribute("data-value") === e) return t(n[r]);
                return t()
            },
            getItem: function(t) {
                return this.getElementWithValue(t, this.$control.children())
            },
            addItems: function(e, n) {
                for (var r = t.isArray(e) ? e : [e], i = 0, o = r.length; o > i; i++) this.isPending = o - 1 > i, this.addItem(r[i], n)
            },
            addItem: function(e, n) {
                var r = n ? [] : ["change"];
                $(this, r, function() {
                    var r, i, o, a, s, u = this,
                        l = u.settings.mode;
                    return e = T(e), -1 !== u.items.indexOf(e) ? void("single" === l && u.close()) : void(u.options.hasOwnProperty(e) && ("single" === l && u.clear(), "multi" === l && u.isFull() || (r = t(u.render("item", u.options[e])), s = u.isFull(), u.items.splice(u.caretPos, 0, e), u.insertAtCaret(r), (!u.isPending || !s && u.isFull()) && u.refreshState(), u.isSetup && (o = u.$dropdown_content.find("[data-selectable]"), u.isPending || (i = u.getOption(e), a = u.getAdjacentOption(i, 1).attr("data-value"), u.refreshOptions(u.isFocused && "single" !== l), a && u.setActiveOption(u.getOption(a))), !o.length || u.isFull() ? u.close() : u.positionDropdown(), u.updatePlaceholder(), u.trigger("item_add", e, r), u.updateOriginalInput({
                        silent: n
                    })))))
                })
            },
            removeItem: function(t, e) {
                var n, r, i, o = this;
                n = "object" == typeof t ? t : o.getItem(t), t = T(n.attr("data-value")), r = o.items.indexOf(t), -1 !== r && (n.remove(), n.hasClass("active") && (i = o.$activeItems.indexOf(n[0]), o.$activeItems.splice(i, 1)), o.items.splice(r, 1), o.lastQuery = null, !o.settings.persist && o.userOptions.hasOwnProperty(t) && o.removeOption(t, e), r < o.caretPos && o.setCaret(o.caretPos - 1), o.refreshState(), o.updatePlaceholder(), o.updateOriginalInput({
                    silent: e
                }), o.positionDropdown(), o.trigger("item_remove", t, n))
            },
            createItem: function(e, n) {
                var r = this,
                    i = r.caretPos;
                e = e || t.trim(r.$control_input.val() || "");
                var o = arguments[arguments.length - 1];
                if ("function" != typeof o && (o = function() {}), "boolean" != typeof n && (n = !0), !r.canCreate(e)) return o(), !1;
                r.lock();
                var a = "function" == typeof r.settings.create ? this.settings.create : function(t) {
                        var e = {};
                        return e[r.settings.labelField] = t, e[r.settings.valueField] = t, e
                    },
                    s = N(function(t) {
                        if (r.unlock(), !t || "object" != typeof t) return o();
                        var e = T(t[r.settings.valueField]);
                        return "string" != typeof e ? o() : (r.setTextboxValue(""), r.addOption(t), r.setCaret(i), r.addItem(e), r.refreshOptions(n && "single" !== r.settings.mode), void o(t))
                    }),
                    u = a.apply(this, [e, s]);
                return "undefined" != typeof u && s(u), !0
            },
            refreshItems: function() {
                this.lastQuery = null, this.isSetup && this.addItem(this.items), this.refreshState(), this.updateOriginalInput()
            },
            refreshState: function() {
                var t, e = this;
                e.isRequired && (e.items.length && (e.isInvalid = !1), e.$control_input.prop("required", t)), e.refreshClasses()
            },
            refreshClasses: function() {
                var e = this,
                    n = e.isFull(),
                    r = e.isLocked;
                e.$wrapper.toggleClass("rtl", e.rtl), e.$control.toggleClass("focus", e.isFocused).toggleClass("disabled", e.isDisabled).toggleClass("required", e.isRequired).toggleClass("invalid", e.isInvalid).toggleClass("locked", r).toggleClass("full", n).toggleClass("not-full", !n).toggleClass("input-active", e.isFocused && !e.isInputHidden).toggleClass("dropdown-active", e.isOpen).toggleClass("has-options", !t.isEmptyObject(e.options)).toggleClass("has-items", e.items.length > 0), e.$control_input.data("grow", !n && !r)
            },
            isFull: function() {
                return null !== this.settings.maxItems && this.items.length >= this.settings.maxItems
            },
            updateOriginalInput: function(t) {
                var e, n, r, i, o = this;
                if (t = t || {}, o.tagType === x) {
                    for (r = [], e = 0, n = o.items.length; n > e; e++) i = o.options[o.items[e]][o.settings.labelField] || "", r.push('<option value="' + S(o.items[e]) + '" selected="selected">' + S(i) + "</option>");
                    r.length || this.$input.attr("multiple") || r.push('<option value="" selected="selected"></option>'), o.$input.html(r.join(""))
                } else o.$input.val(o.getValue()), o.$input.attr("value", o.$input.val());
                o.isSetup && (t.silent || o.trigger("change", o.$input.val()))
            },
            updatePlaceholder: function() {
                if (this.settings.placeholder) {
                    var t = this.$control_input;
                    this.items.length ? t.removeAttr("placeholder") : t.attr("placeholder", this.settings.placeholder), t.triggerHandler("update", {
                        force: !0
                    })
                }
            },
            open: function() {
                var t = this;
                t.isLocked || t.isOpen || "multi" === t.settings.mode && t.isFull() || (t.focus(), t.isOpen = !0, t.refreshState(), t.$dropdown.css({
                    visibility: "hidden",
                    display: "block"
                }), t.positionDropdown(), t.$dropdown.css({
                    visibility: "visible"
                }), t.trigger("dropdown_open", t.$dropdown))
            },
            close: function() {
                var t = this,
                    e = t.isOpen;
                "single" === t.settings.mode && t.items.length && t.hideInput(), t.isOpen = !1, t.$dropdown.hide(), t.setActiveOption(null), t.refreshState(), e && t.trigger("dropdown_close", t.$dropdown)
            },
            positionDropdown: function() {
                var t = this.$control,
                    e = "body" === this.settings.dropdownParent ? t.offset() : t.position();
                e.top += t.outerHeight(!0), this.$dropdown.css({
                    width: t.outerWidth(),
                    top: e.top,
                    left: e.left
                })
            },
            clear: function(t) {
                var e = this;
                e.items.length && (e.$control.children(":not(input)").remove(), e.items = [], e.lastQuery = null, e.setCaret(0), e.setActiveItem(null), e.updatePlaceholder(), e.updateOriginalInput({
                    silent: t
                }), e.refreshState(), e.showInput(), e.trigger("clear"))
            },
            insertAtCaret: function(e) {
                var n = Math.min(this.caretPos, this.items.length);
                0 === n ? this.$control.prepend(e) : t(this.$control[0].childNodes[n]).before(e), this.setCaret(n + 1)
            },
            deleteSelection: function(e) {
                var n, r, i, o, a, s, u, l, c, f = this;
                if (i = e && e.keyCode === g ? -1 : 1, o = D(f.$control_input[0]), f.$activeOption && !f.settings.hideSelected && (u = f.getAdjacentOption(f.$activeOption, -1).attr("data-value")), a = [], f.$activeItems.length) {
                    for (c = f.$control.children(".active:" + (i > 0 ? "last" : "first")), s = f.$control.children(":not(input)").index(c), i > 0 && s++, n = 0, r = f.$activeItems.length; r > n; n++) a.push(t(f.$activeItems[n]).attr("data-value"));
                    e && (e.preventDefault(), e.stopPropagation())
                } else(f.isFocused || "single" === f.settings.mode) && f.items.length && (0 > i && 0 === o.start && 0 === o.length ? a.push(f.items[f.caretPos - 1]) : i > 0 && o.start === f.$control_input.val().length && a.push(f.items[f.caretPos]));
                if (!a.length || "function" == typeof f.settings.onDelete && f.settings.onDelete.apply(f, [a]) === !1) return !1;
                for ("undefined" != typeof s && f.setCaret(s); a.length;) f.removeItem(a.pop());
                return f.showInput(), f.positionDropdown(), f.refreshOptions(!0), u && (l = f.getOption(u), l.length && f.setActiveOption(l)), !0
            },
            advanceSelection: function(t, e) {
                var n, r, i, o, a, s, u = this;
                0 !== t && (u.rtl && (t *= -1), n = t > 0 ? "last" : "first", r = D(u.$control_input[0]), u.isFocused && !u.isInputHidden ? (o = u.$control_input.val().length, a = 0 > t ? 0 === r.start && 0 === r.length : r.start === o, a && !o && u.advanceCaret(t, e)) : (s = u.$control.children(".active:" + n), s.length && (i = u.$control.children(":not(input)").index(s), u.setActiveItem(null), u.setCaret(t > 0 ? i + 1 : i))))
            },
            advanceCaret: function(t, e) {
                var n, r, i = this;
                0 !== t && (n = t > 0 ? "next" : "prev", i.isShiftDown ? (r = i.$control_input[n](), r.length && (i.hideInput(), i.setActiveItem(r), e && e.preventDefault())) : i.setCaret(i.caretPos + t))
            },
            setCaret: function(e) {
                var n = this;
                if (e = "single" === n.settings.mode ? n.items.length : Math.max(0, Math.min(n.items.length, e)), !n.isPending) {
                    var r, i, o, a;
                    for (o = n.$control.children(":not(input)"), r = 0, i = o.length; i > r; r++) a = t(o[r]).detach(), e > r ? n.$control_input.before(a) : n.$control.append(a)
                }
                n.caretPos = e
            },
            lock: function() {
                this.close(), this.isLocked = !0, this.refreshState()
            },
            unlock: function() {
                this.isLocked = !1, this.refreshState()
            },
            disable: function() {
                var t = this;
                t.$input.prop("disabled", !0), t.$control_input.prop("disabled", !0).prop("tabindex", -1), t.isDisabled = !0, t.lock()
            },
            enable: function() {
                var t = this;
                t.$input.prop("disabled", !1), t.$control_input.prop("disabled", !1).prop("tabindex", t.tabIndex), t.isDisabled = !1, t.unlock()
            },
            destroy: function() {
                var e = this,
                    n = e.eventNS,
                    r = e.revertSettings;
                e.trigger("destroy"), e.off(), e.$wrapper.remove(), e.$dropdown.remove(), e.$input.html("").append(r.$children).removeAttr("tabindex").removeClass("selectized").attr({
                    tabindex: r.tabindex
                }).show(), e.$control_input.removeData("grow"), e.$input.removeData("selectize"), t(window).off(n), t(document).off(n), t(document.body).off(n), delete e.$input[0].selectize
            },
            render: function(t, e) {
                var n, r, i = "",
                    o = !1,
                    a = this,
                    s = /^[\t \r\n]*<([a-z][a-z0-9\-_]*(?:\:[a-z][a-z0-9\-_]*)?)/i;
                return ("option" === t || "item" === t) && (n = T(e[a.settings.valueField]), o = !!n), o && (k(a.renderCache[t]) || (a.renderCache[t] = {}), a.renderCache[t].hasOwnProperty(n)) ? a.renderCache[t][n] : (i = a.settings.render[t].apply(this, [e, S]), ("option" === t || "option_create" === t) && (i = i.replace(s, "<$1 data-selectable")), "optgroup" === t && (r = e[a.settings.optgroupValueField] || "", i = i.replace(s, '<$1 data-group="' + j(S(r)) + '"')), ("option" === t || "item" === t) && (i = i.replace(s, '<$1 data-value="' + j(S(n || "")) + '"')), o && (a.renderCache[t][n] = i), i)
            },
            clearCache: function(t) {
                var e = this;
                "undefined" == typeof t ? e.renderCache = {} : delete e.renderCache[t]
            },
            canCreate: function(t) {
                var e = this;
                if (!e.settings.create) return !1;
                var n = e.settings.createFilter;
                return !(!t.length || "function" == typeof n && !n.apply(e, [t]) || "string" == typeof n && !new RegExp(n).test(t) || n instanceof RegExp && !n.test(t))
            }
        }), R.count = 0, R.defaults = {
            options: [],
            optgroups: [],
            plugins: [],
            delimiter: ",",
            splitOn: null,
            persist: !0,
            diacritics: !0,
            create: !1,
            createOnBlur: !1,
            createFilter: null,
            highlight: !0,
            openOnFocus: !0,
            maxOptions: 1e3,
            maxItems: null,
            hideSelected: null,
            addPrecedence: !1,
            selectOnTab: !1,
            preload: !1,
            allowEmptyOption: !1,
            closeAfterSelect: !1,
            scrollDuration: 60,
            loadThrottle: 300,
            loadingClass: "loading",
            dataAttr: "data-data",
            optgroupField: "optgroup",
            valueField: "value",
            labelField: "text",
            optgroupLabelField: "label",
            optgroupValueField: "value",
            lockOptgroupOrder: !1,
            sortField: "$order",
            searchField: ["text"],
            searchConjunction: "and",
            mode: null,
            wrapperClass: "selectize-control",
            inputClass: "selectize-input",
            dropdownClass: "selectize-dropdown",
            dropdownContentClass: "selectize-dropdown-content",
            dropdownParent: null,
            copyClassesToDropdown: !0,
            render: {}
        }, t.fn.selectize = function(e) {
            var n = t.fn.selectize.defaults,
                r = t.extend({}, n, e),
                i = r.dataAttr,
                o = r.labelField,
                a = r.valueField,
                s = r.optgroupField,
                u = r.optgroupLabelField,
                l = r.optgroupValueField,
                c = {},
                f = function(e, n) {
                    var s, u, l, c, f = e.attr(i);
                    if (f)
                        for (n.options = JSON.parse(f), s = 0, u = n.options.length; u > s; s++) n.items.push(n.options[s][a]);
                    else {
                        var d = t.trim(e.val() || "");
                        if (!r.allowEmptyOption && !d.length) return;
                        for (l = d.split(r.delimiter), s = 0, u = l.length; u > s; s++) c = {}, c[o] = l[s], c[a] = l[s], n.options.push(c);
                        n.items = l
                    }
                },
                d = function(e, n) {
                    var f, d, p, h, g = n.options,
                        m = function(t) {
                            var e = i && t.attr(i);
                            return "string" == typeof e && e.length ? JSON.parse(e) : null
                        },
                        v = function(e, i) {
                            e = t(e);
                            var u = T(e.attr("value"));
                            if (u || r.allowEmptyOption)
                                if (c.hasOwnProperty(u)) {
                                    if (i) {
                                        var l = c[u][s];
                                        l ? t.isArray(l) ? l.push(i) : c[u][s] = [l, i] : c[u][s] = i
                                    }
                                } else {
                                    var f = m(e) || {};
                                    f[o] = f[o] || e.text(), f[a] = f[a] || u, f[s] = f[s] || i, c[u] = f, g.push(f), e.is(":selected") && n.items.push(u)
                                }
                        },
                        y = function(e) {
                            var r, i, o, a, s;
                            for (e = t(e), o = e.attr("label"), o && (a = m(e) || {}, a[u] = o, a[l] = o, n.optgroups.push(a)), s = t("option", e), r = 0, i = s.length; i > r; r++) v(s[r], o)
                        };
                    for (n.maxItems = e.attr("multiple") ? null : 1, h = e.children(), f = 0, d = h.length; d > f; f++) p = h[f].tagName.toLowerCase(), "optgroup" === p ? y(h[f]) : "option" === p && v(h[f])
                };
            return this.each(function() {
                if (!this.selectize) {
                    var i, o = t(this),
                        a = this.tagName.toLowerCase(),
                        s = o.attr("placeholder") || o.attr("data-placeholder");
                    s || r.allowEmptyOption || (s = o.children('option[value=""]').text());
                    var u = {
                        placeholder: s,
                        options: [],
                        optgroups: [],
                        items: []
                    };
                    "select" === a ? d(o, u) : f(o, u), i = new R(o, t.extend(!0, {}, n, u, e))
                }
            })
        }, t.fn.selectize.defaults = R.defaults, t.fn.selectize.support = {
            validity: C
        }, R.define("drag_drop", function() {
            if (!t.fn.sortable) throw new Error('The "drag_drop" plugin requires jQuery UI "sortable".');
            if ("multi" === this.settings.mode) {
                var e = this;
                e.lock = function() {
                    var t = e.lock;
                    return function() {
                        var n = e.$control.data("sortable");
                        return n && n.disable(), t.apply(e, arguments)
                    }
                }(), e.unlock = function() {
                    var t = e.unlock;
                    return function() {
                        var n = e.$control.data("sortable");
                        return n && n.enable(), t.apply(e, arguments)
                    }
                }(), e.setup = function() {
                    var n = e.setup;
                    return function() {
                        n.apply(this, arguments);
                        var r = e.$control.sortable({
                            items: "[data-value]",
                            forcePlaceholderSize: !0,
                            disabled: e.isLocked,
                            start: function(t, e) {
                                e.placeholder.css("width", e.helper.css("width")), r.css({
                                    overflow: "visible"
                                })
                            },
                            stop: function() {
                                r.css({
                                    overflow: "hidden"
                                });
                                var n = e.$activeItems ? e.$activeItems.slice() : null,
                                    i = [];
                                r.children("[data-value]").each(function() {
                                    i.push(t(this).attr("data-value"))
                                }), e.setValue(i), e.setActiveItem(n)
                            }
                        })
                    }
                }()
            }
        }), R.define("dropdown_header", function(e) {
            var n = this;
            e = t.extend({
                title: "Untitled",
                headerClass: "selectize-dropdown-header",
                titleRowClass: "selectize-dropdown-header-title",
                labelClass: "selectize-dropdown-header-label",
                closeClass: "selectize-dropdown-header-close",
                html: function(t) {
                    return '<div class="' + t.headerClass + '"><div class="' + t.titleRowClass + '"><span class="' + t.labelClass + '">' + t.title + '</span><a href="javascript:void(0)" class="' + t.closeClass + '">&times;</a></div></div>'
                }
            }, e), n.setup = function() {
                var r = n.setup;
                return function() {
                    r.apply(n, arguments), n.$dropdown_header = t(e.html(e)), n.$dropdown.prepend(n.$dropdown_header)
                }
            }()
        }), R.define("optgroup_columns", function(e) {
            var n = this;
            e = t.extend({
                equalizeWidth: !0,
                equalizeHeight: !0
            }, e), this.getAdjacentOption = function(e, n) {
                var r = e.closest("[data-group]").find("[data-selectable]"),
                    i = r.index(e) + n;
                return i >= 0 && i < r.length ? r.eq(i) : t()
            }, this.onKeyDown = function() {
                var t = n.onKeyDown;
                return function(e) {
                    var r, i, o, a;
                    return !this.isOpen || e.keyCode !== l && e.keyCode !== d ? t.apply(this, arguments) : (n.ignoreHover = !0, a = this.$activeOption.closest("[data-group]"), r = a.find("[data-selectable]").index(this.$activeOption), a = e.keyCode === l ? a.prev("[data-group]") : a.next("[data-group]"), o = a.find("[data-selectable]"), i = o.eq(Math.min(o.length - 1, r)), void(i.length && this.setActiveOption(i)))
                }
            }();
            var r = function() {
                    var t, e = r.width,
                        n = document;
                    return "undefined" == typeof e && (t = n.createElement("div"), t.innerHTML = '<div style="width:50px;height:50px;position:absolute;left:-50px;top:-50px;overflow:auto;"><div style="width:1px;height:100px;"></div></div>', t = t.firstChild, n.body.appendChild(t), e = r.width = t.offsetWidth - t.clientWidth, n.body.removeChild(t)), e
                },
                i = function() {
                    var i, o, a, s, u, l, c;
                    if (c = t("[data-group]", n.$dropdown_content), o = c.length, o && n.$dropdown_content.width()) {
                        if (e.equalizeHeight) {
                            for (a = 0, i = 0; o > i; i++) a = Math.max(a, c.eq(i).height());
                            c.css({
                                height: a
                            })
                        }
                        e.equalizeWidth && (l = n.$dropdown_content.innerWidth() - r(), s = Math.round(l / o), c.css({
                            width: s
                        }), o > 1 && (u = l - s * (o - 1), c.eq(o - 1).css({
                            width: u
                        })))
                    }
                };
            (e.equalizeHeight || e.equalizeWidth) && (E.after(this, "positionDropdown", i), E.after(this, "refreshOptions", i))
        }), R.define("remove_button", function(e) {
            if ("single" !== this.settings.mode) {
                e = t.extend({
                    label: "&times;",
                    title: "Remove",
                    className: "remove",
                    append: !0
                }, e);
                var n = this,
                    r = '<a href="javascript:void(0)" class="' + e.className + '" tabindex="-1" title="' + S(e.title) + '">' + e.label + "</a>",
                    i = function(t, e) {
                        var n = t.search(/(<\/[^>]+>\s*)$/);
                        return t.substring(0, n) + e + t.substring(n)
                    };
                this.setup = function() {
                    var o = n.setup;
                    return function() {
                        if (e.append) {
                            var a = n.settings.render.item;
                            n.settings.render.item = function() {
                                return i(a.apply(this, arguments), r)
                            }
                        }
                        o.apply(this, arguments), this.$control.on("click", "." + e.className, function(e) {
                            if (e.preventDefault(), !n.isLocked) {
                                var r = t(e.currentTarget).parent();
                                n.setActiveItem(r), n.deleteSelection() && n.setCaret(n.items.length)
                            }
                        })
                    }
                }()
            }
        }), R.define("restore_on_backspace", function(t) {
            var e = this;
            t.text = t.text || function(t) {
                return t[this.settings.labelField]
            }, this.onKeyDown = function() {
                var n = e.onKeyDown;
                return function(e) {
                    var r, i;
                    return e.keyCode === g && "" === this.$control_input.val() && !this.$activeItems.length && (r = this.caretPos - 1, r >= 0 && r < this.items.length) ? (i = this.options[this.items[r]], this.deleteSelection(e) && (this.setTextboxValue(t.text.apply(this, [i])), this.refreshOptions(!0)), void e.preventDefault()) : n.apply(this, arguments)
                }
            }()
        }), R
    }), ! function(t) {
        "undefined" != typeof exports ? t(exports) : (window.hljs = t({}), "function" == typeof define && define.amd && define([], function() {
            return window.hljs
        }))
    }(function(t) {
        function e(t) {
            return t.replace(/&/gm, "&amp;").replace(/</gm, "&lt;").replace(/>/gm, "&gt;")
        }

        function n(t) {
            return t.nodeName.toLowerCase()
        }

        function r(t, e) {
            var n = t && t.exec(e);
            return n && 0 == n.index
        }

        function i(t) {
            var e = (t.className + " " + (t.parentNode ? t.parentNode.className : "")).split(/\s+/);
            return e = e.map(function(t) {
                return t.replace(/^lang(uage)?-/, "")
            }), e.filter(function(t) {
                return b(t) || /no(-?)highlight|plain|text/.test(t)
            })[0]
        }

        function o(t, e) {
            var n, r = {};
            for (n in t) r[n] = t[n];
            if (e)
                for (n in e) r[n] = e[n];
            return r
        }

        function a(t) {
            var e = [];
            return function r(t, i) {
                for (var o = t.firstChild; o; o = o.nextSibling) 3 == o.nodeType ? i += o.nodeValue.length : 1 == o.nodeType && (e.push({
                    event: "start",
                    offset: i,
                    node: o
                }), i = r(o, i), n(o).match(/br|hr|img|input/) || e.push({
                    event: "stop",
                    offset: i,
                    node: o
                }));
                return i
            }(t, 0), e
        }

        function s(t, r, i) {
            function o() {
                return t.length && r.length ? t[0].offset != r[0].offset ? t[0].offset < r[0].offset ? t : r : "start" == r[0].event ? t : r : t.length ? t : r
            }

            function a(t) {
                function r(t) {
                    return " " + t.nodeName + '="' + e(t.value) + '"'
                }
                c += "<" + n(t) + Array.prototype.map.call(t.attributes, r).join("") + ">"
            }

            function s(t) {
                c += "</" + n(t) + ">"
            }

            function u(t) {
                ("start" == t.event ? a : s)(t.node)
            }
            for (var l = 0, c = "", f = []; t.length || r.length;) {
                var d = o();
                if (c += e(i.substr(l, d[0].offset - l)), l = d[0].offset, d == t) {
                    f.reverse().forEach(s);
                    do u(d.splice(0, 1)[0]), d = o(); while (d == t && d.length && d[0].offset == l);
                    f.reverse().forEach(a)
                } else "start" == d[0].event ? f.push(d[0].node) : f.pop(), u(d.splice(0, 1)[0])
            }
            return c + e(i.substr(l))
        }

        function u(t) {
            function e(t) {
                return t && t.source || t
            }

            function n(n, r) {
                return new RegExp(e(n), "m" + (t.cI ? "i" : "") + (r ? "g" : ""))
            }

            function r(i, a) {
                if (!i.compiled) {
                    if (i.compiled = !0, i.k = i.k || i.bK, i.k) {
                        var s = {},
                            u = function(e, n) {
                                t.cI && (n = n.toLowerCase()), n.split(" ").forEach(function(t) {
                                    var n = t.split("|");
                                    s[n[0]] = [e, n[1] ? Number(n[1]) : 1]
                                })
                            };
                        "string" == typeof i.k ? u("keyword", i.k) : Object.keys(i.k).forEach(function(t) {
                            u(t, i.k[t])
                        }), i.k = s
                    }
                    i.lR = n(i.l || /\b\w+\b/, !0), a && (i.bK && (i.b = "\\b(" + i.bK.split(" ").join("|") + ")\\b"), i.b || (i.b = /\B|\b/), i.bR = n(i.b), i.e || i.eW || (i.e = /\B|\b/), i.e && (i.eR = n(i.e)), i.tE = e(i.e) || "", i.eW && a.tE && (i.tE += (i.e ? "|" : "") + a.tE)), i.i && (i.iR = n(i.i)), void 0 === i.r && (i.r = 1), i.c || (i.c = []);
                    var l = [];
                    i.c.forEach(function(t) {
                        t.v ? t.v.forEach(function(e) {
                            l.push(o(t, e))
                        }) : l.push("self" == t ? i : t)
                    }), i.c = l, i.c.forEach(function(t) {
                        r(t, i)
                    }), i.starts && r(i.starts, a);
                    var c = i.c.map(function(t) {
                        return t.bK ? "\\.?(" + t.b + ")\\.?" : t.b
                    }).concat([i.tE, i.i]).map(e).filter(Boolean);
                    i.t = c.length ? n(c.join("|"), !0) : {
                        exec: function() {
                            return null
                        }
                    }
                }
            }
            r(t)
        }

        function l(t, n, i, o) {
            function a(t, e) {
                for (var n = 0; n < e.c.length; n++)
                    if (r(e.c[n].bR, t)) return e.c[n]
            }

            function s(t, e) {
                if (r(t.eR, e)) {
                    for (; t.endsParent && t.parent;) t = t.parent;
                    return t
                }
                return t.eW ? s(t.parent, e) : void 0
            }

            function f(t, e) {
                return !i && r(e.iR, t)
            }

            function d(t, e) {
                var n = _.cI ? e[0].toLowerCase() : e[0];
                return t.k.hasOwnProperty(n) && t.k[n]
            }

            function p(t, e, n, r) {
                var i = r ? "" : w.classPrefix,
                    o = '<span class="' + i,
                    a = n ? "" : "</span>";
                return o += t + '">', o + e + a
            }

            function h() {
                if (!k.k) return e(j);
                var t = "",
                    n = 0;
                k.lR.lastIndex = 0;
                for (var r = k.lR.exec(j); r;) {
                    t += e(j.substr(n, r.index - n));
                    var i = d(k, r);
                    i ? (E += i[1], t += p(i[0], e(r[0]))) : t += e(r[0]), n = k.lR.lastIndex, r = k.lR.exec(j)
                }
                return t + e(j.substr(n))
            }

            function g() {
                if (k.sL && !x[k.sL]) return e(j);
                var t = k.sL ? l(k.sL, j, !0, T[k.sL]) : c(j);
                return k.r > 0 && (E += t.r), "continuous" == k.subLanguageMode && (T[k.sL] = t.top), p(t.language, t.value, !1, !0)
            }

            function m() {
                return void 0 !== k.sL ? g() : h()
            }

            function v(t, n) {
                var r = t.cN ? p(t.cN, "", !0) : "";
                t.rB ? (S += r, j = "") : t.eB ? (S += e(n) + r, j = "") : (S += r, j = n), k = Object.create(t, {
                    parent: {
                        value: k
                    }
                })
            }

            function y(t, n) {
                if (j += t, void 0 === n) return S += m(), 0;
                var r = a(n, k);
                if (r) return S += m(), v(r, n), r.rB ? 0 : n.length;
                var i = s(k, n);
                if (i) {
                    var o = k;
                    o.rE || o.eE || (j += n), S += m();
                    do k.cN && (S += "</span>"), E += k.r, k = k.parent; while (k != i.parent);
                    return o.eE && (S += e(n)), j = "", i.starts && v(i.starts, ""), o.rE ? 0 : n.length
                }
                if (f(n, k)) throw new Error('Illegal lexeme "' + n + '" for mode "' + (k.cN || "<unnamed>") + '"');
                return j += n, n.length || 1
            }
            var _ = b(t);
            if (!_) throw new Error('Unknown language: "' + t + '"');
            u(_);
            var C, k = o || _,
                T = {},
                S = "";
            for (C = k; C != _; C = C.parent) C.cN && (S = p(C.cN, "", !0) + S);
            var j = "",
                E = 0;
            try {
                for (var N, A, $ = 0; k.t.lastIndex = $, N = k.t.exec(n), N;) A = y(n.substr($, N.index - $), N[0]), $ = N.index + A;
                for (y(n.substr($)), C = k; C.parent; C = C.parent) C.cN && (S += "</span>");
                return {
                    r: E,
                    value: S,
                    language: t,
                    top: k
                }
            } catch (O) {
                if (-1 != O.message.indexOf("Illegal")) return {
                    r: 0,
                    value: e(n)
                };
                throw O
            }
        }

        function c(t, n) {
            n = n || w.languages || Object.keys(x);
            var r = {
                    r: 0,
                    value: e(t)
                },
                i = r;
            return n.forEach(function(e) {
                if (b(e)) {
                    var n = l(e, t, !1);
                    n.language = e, n.r > i.r && (i = n), n.r > r.r && (i = r, r = n)
                }
            }), i.language && (r.second_best = i), r
        }

        function f(t) {
            return w.tabReplace && (t = t.replace(/^((<[^>]+>|\t)+)/gm, function(t, e) {
                return e.replace(/\t/g, w.tabReplace)
            })), w.useBR && (t = t.replace(/\n/g, "<br>")), t
        }

        function d(t, e, n) {
            var r = e ? _[e] : n,
                i = [t.trim()];
            return t.match(/\bhljs\b/) || i.push("hljs"), -1 === t.indexOf(r) && i.push(r), i.join(" ").trim()
        }

        function p(t) {
            var e = i(t);
            if (!/no(-?)highlight|plain|text/.test(e)) {
                var n;
                w.useBR ? (n = document.createElementNS("http://www.w3.org/1999/xhtml", "div"), n.innerHTML = t.innerHTML.replace(/\n/g, "").replace(/<br[ \/]*>/g, "\n")) : n = t;
                var r = n.textContent,
                    o = e ? l(e, r, !0) : c(r),
                    u = a(n);
                if (u.length) {
                    var p = document.createElementNS("http://www.w3.org/1999/xhtml", "div");
                    p.innerHTML = o.value, o.value = s(u, a(p), r)
                }
                o.value = f(o.value), t.innerHTML = o.value, t.className = d(t.className, e, o.language), t.result = {
                    language: o.language,
                    re: o.r
                }, o.second_best && (t.second_best = {
                    language: o.second_best.language,
                    re: o.second_best.r
                })
            }
        }

        function h(t) {
            w = o(w, t)
        }

        function g() {
            if (!g.called) {
                g.called = !0;
                var t = document.querySelectorAll("pre code");
                Array.prototype.forEach.call(t, p)
            }
        }

        function m() {
            addEventListener("DOMContentLoaded", g, !1), addEventListener("load", g, !1)
        }

        function v(e, n) {
            var r = x[e] = n(t);
            r.aliases && r.aliases.forEach(function(t) {
                _[t] = e
            })
        }

        function y() {
            return Object.keys(x)
        }

        function b(t) {
            return x[t] || x[_[t]]
        }
        var w = {
                classPrefix: "hljs-",
                tabReplace: null,
                useBR: !1,
                languages: void 0
            },
            x = {},
            _ = {};
        return t.highlight = l, t.highlightAuto = c, t.fixMarkup = f, t.highlightBlock = p, t.configure = h, t.initHighlighting = g, t.initHighlightingOnLoad = m, t.registerLanguage = v, t.listLanguages = y, t.getLanguage = b, t.inherit = o, t.IR = "[a-zA-Z]\\w*", t.UIR = "[a-zA-Z_]\\w*", t.NR = "\\b\\d+(\\.\\d+)?", t.CNR = "\\b(0[xX][a-fA-F0-9]+|(\\d+(\\.\\d*)?|\\.\\d+)([eE][-+]?\\d+)?)", t.BNR = "\\b(0b[01]+)", t.RSR = "!|!=|!==|%|%=|&|&&|&=|\\*|\\*=|\\+|\\+=|,|-|-=|/=|/|:|;|<<|<<=|<=|<|===|==|=|>>>=|>>=|>=|>>>|>>|>|\\?|\\[|\\{|\\(|\\^|\\^=|\\||\\|=|\\|\\||~", t.BE = {
            b: "\\\\[\\s\\S]",
            r: 0
        }, t.ASM = {
            cN: "string",
            b: "'",
            e: "'",
            i: "\\n",
            c: [t.BE]
        }, t.QSM = {
            cN: "string",
            b: '"',
            e: '"',
            i: "\\n",
            c: [t.BE]
        }, t.PWM = {
            b: /\b(a|an|the|are|I|I'm|isn't|don't|doesn't|won't|but|just|should|pretty|simply|enough|gonna|going|wtf|so|such)\b/
        }, t.C = function(e, n, r) {
            var i = t.inherit({
                cN: "comment",
                b: e,
                e: n,
                c: []
            }, r || {});
            return i.c.push(t.PWM), i
        }, t.CLCM = t.C("//", "$"), t.CBCM = t.C("/\\*", "\\*/"), t.HCM = t.C("#", "$"), t.NM = {
            cN: "number",
            b: t.NR,
            r: 0
        }, t.CNM = {
            cN: "number",
            b: t.CNR,
            r: 0
        }, t.BNM = {
            cN: "number",
            b: t.BNR,
            r: 0
        }, t.CSSNM = {
            cN: "number",
            b: t.NR + "(%|em|ex|ch|rem|vw|vh|vmin|vmax|cm|mm|in|pt|pc|px|deg|grad|rad|turn|s|ms|Hz|kHz|dpi|dpcm|dppx)?",
            r: 0
        }, t.RM = {
            cN: "regexp",
            b: /\//,
            e: /\/[gimuy]*/,
            i: /\n/,
            c: [t.BE, {
                b: /\[/,
                e: /\]/,
                r: 0,
                c: [t.BE]
            }]
        }, t.TM = {
            cN: "title",
            b: t.IR,
            r: 0
        }, t.UTM = {
            cN: "title",
            b: t.UIR,
            r: 0
        }, t
    }), hljs.registerLanguage("xml", function(t) {
        var e = "[A-Za-z0-9\\._:-]+",
            n = {
                b: /<\?(php)?(?!\w)/,
                e: /\?>/,
                sL: "php",
                subLanguageMode: "continuous"
            },
            r = {
                eW: !0,
                i: /</,
                r: 0,
                c: [n, {
                    cN: "attribute",
                    b: e,
                    r: 0
                }, {
                    b: "=",
                    r: 0,
                    c: [{
                        cN: "value",
                        c: [n],
                        v: [{
                            b: /"/,
                            e: /"/
                        }, {
                            b: /'/,
                            e: /'/
                        }, {
                            b: /[^\s\/>]+/
                        }]
                    }]
                }]
            };
        return {
            aliases: ["html", "xhtml", "rss", "atom", "xsl", "plist"],
            cI: !0,
            c: [{
                cN: "doctype",
                b: "<!DOCTYPE",
                e: ">",
                r: 10,
                c: [{
                    b: "\\[",
                    e: "\\]"
                }]
            }, t.C("<!--", "-->", {
                r: 10
            }), {
                cN: "cdata",
                b: "<\\!\\[CDATA\\[",
                e: "\\]\\]>",
                r: 10
            }, {
                cN: "tag",
                b: "<style(?=\\s|>|$)",
                e: ">",
                k: {
                    title: "style"
                },
                c: [r],
                starts: {
                    e: "</style>",
                    rE: !0,
                    sL: "css"
                }
            }, {
                cN: "tag",
                b: "<script(?=\\s|>|$)",
                e: ">",
                k: {
                    title: "script"
                },
                c: [r],
                starts: {
                    e: "</script>",
                    rE: !0,
                    sL: ""
                }
            }, n, {
                cN: "pi",
                b: /<\?\w+/,
                e: /\?>/,
                r: 10
            }, {
                cN: "tag",
                b: "</?",
                e: "/?>",
                c: [{
                    cN: "title",
                    b: /[^ \/><\n\t]+/,
                    r: 0
                }, r]
            }]
        }
    }), hljs.registerLanguage("css", function(t) {
        var e = "[a-zA-Z-][a-zA-Z0-9_-]*",
            n = {
                cN: "function",
                b: e + "\\(",
                rB: !0,
                eE: !0,
                e: "\\("
            },
            r = {
                cN: "rule",
                b: /[A-Z\_\.\-]+\s*:/,
                rB: !0,
                e: ";",
                eW: !0,
                c: [{
                    cN: "attribute",
                    b: /\S/,
                    e: ":",
                    eE: !0,
                    starts: {
                        cN: "value",
                        eW: !0,
                        eE: !0,
                        c: [n, t.CSSNM, t.QSM, t.ASM, t.CBCM, {
                            cN: "hexcolor",
                            b: "#[0-9A-Fa-f]+"
                        }, {
                            cN: "important",
                            b: "!important"
                        }]
                    }
                }]
            };
        return {
            cI: !0,
            i: /[=\/|']/,
            c: [t.CBCM, r, {
                cN: "id",
                b: /\#[A-Za-z0-9_-]+/
            }, {
                cN: "class",
                b: /\.[A-Za-z0-9_-]+/,
                r: 0
            }, {
                cN: "attr_selector",
                b: /\[/,
                e: /\]/,
                i: "$"
            }, {
                cN: "pseudo",
                b: /:(:)?[a-zA-Z0-9\_\-\+\(\)"']+/
            }, {
                cN: "at_rule",
                b: "@(font-face|page)",
                l: "[a-z-]+",
                k: "font-face page"
            }, {
                cN: "at_rule",
                b: "@",
                e: "[{;]",
                c: [{
                    cN: "keyword",
                    b: /\S+/
                }, {
                    b: /\s/,
                    eW: !0,
                    eE: !0,
                    r: 0,
                    c: [n, t.ASM, t.QSM, t.CSSNM]
                }]
            }, {
                cN: "tag",
                b: e,
                r: 0
            }, {
                cN: "rules",
                b: "{",
                e: "}",
                i: /\S/,
                r: 0,
                c: [t.CBCM, r]
            }]
        }
    }), hljs.registerLanguage("javascript", function(t) {
        return {
            aliases: ["js"],
            k: {
                keyword: "in of if for while finally var new function do return void else break catch instanceof with throw case default try this switch continue typeof delete let yield const export super debugger as await",
                literal: "true false null undefined NaN Infinity",
                built_in: "eval isFinite isNaN parseFloat parseInt decodeURI decodeURIComponent encodeURI encodeURIComponent escape unescape Object Function Boolean Error EvalError InternalError RangeError ReferenceError StopIteration SyntaxError TypeError URIError Number Math Date String RegExp Array Float32Array Float64Array Int16Array Int32Array Int8Array Uint16Array Uint32Array Uint8Array Uint8ClampedArray ArrayBuffer DataView JSON Intl arguments require module console window document Symbol Set Map WeakSet WeakMap Proxy Reflect Promise"
            },
            c: [{
                cN: "pi",
                r: 10,
                v: [{
                    b: /^\s*('|")use strict('|")/
                }, {
                    b: /^\s*('|")use asm('|")/
                }]
            }, t.ASM, t.QSM, {
                cN: "string",
                b: "`",
                e: "`",
                c: [t.BE, {
                    cN: "subst",
                    b: "\\$\\{",
                    e: "\\}"
                }]
            }, t.CLCM, t.CBCM, {
                cN: "number",
                b: "\\b(0[xXbBoO][a-fA-F0-9]+|(\\d+(\\.\\d*)?|\\.\\d+)([eE][-+]?\\d+)?)",
                r: 0
            }, {
                b: "(" + t.RSR + "|\\b(case|return|throw)\\b)\\s*",
                k: "return throw case",
                c: [t.CLCM, t.CBCM, t.RM, {
                    b: /</,
                    e: />\s*[);\]]/,
                    r: 0,
                    sL: "xml"
                }],
                r: 0
            }, {
                cN: "function",
                bK: "function",
                e: /\{/,
                eE: !0,
                c: [t.inherit(t.TM, {
                    b: /[A-Za-z$_][0-9A-Za-z$_]*/
                }), {
                    cN: "params",
                    b: /\(/,
                    e: /\)/,
                    c: [t.CLCM, t.CBCM],
                    i: /["'\(]/
                }],
                i: /\[|%/
            }, {
                b: /\$[(.]/
            }, {
                b: "\\." + t.IR,
                r: 0
            }, {
                bK: "import",
                e: "[;$]",
                k: "import from as",
                c: [t.ASM, t.QSM]
            }, {
                cN: "class",
                bK: "class",
                e: /[{;=]/,
                eE: !0,
                i: /[:"\[\]]/,
                c: [{
                    bK: "extends"
                }, t.UTM]
            }]
        }
    }), hljs.registerLanguage("scss", function(t) {
        var e = "[a-zA-Z-][a-zA-Z0-9_-]*",
            n = {
                cN: "variable",
                b: "(\\$" + e + ")\\b"
            },
            r = {
                cN: "function",
                b: e + "\\(",
                rB: !0,
                eE: !0,
                e: "\\("
            },
            i = {
                cN: "hexcolor",
                b: "#[0-9A-Fa-f]+"
            };
        return {
            cN: "attribute",
            b: "[A-Z\\_\\.\\-]+",
            e: ":",
            eE: !0,
            i: "[^\\s]",
            starts: {
                cN: "value",
                eW: !0,
                eE: !0,
                c: [r, i, t.CSSNM, t.QSM, t.ASM, t.CBCM, {
                    cN: "important",
                    b: "!important"
                }]
            }
        }, {
            cI: !0,
            i: "[=/|']",
            c: [t.CLCM, t.CBCM, r, {
                cN: "id",
                b: "\\#[A-Za-z0-9_-]+",
                r: 0
            }, {
                cN: "class",
                b: "\\.[A-Za-z0-9_-]+",
                r: 0
            }, {
                cN: "attr_selector",
                b: "\\[",
                e: "\\]",
                i: "$"
            }, {
                cN: "tag",
                b: "\\b(a|abbr|acronym|address|area|article|aside|audio|b|base|big|blockquote|body|br|button|canvas|caption|cite|code|col|colgroup|command|datalist|dd|del|details|dfn|div|dl|dt|em|embed|fieldset|figcaption|figure|footer|form|frame|frameset|(h[1-6])|head|header|hgroup|hr|html|i|iframe|img|input|ins|kbd|keygen|label|legend|li|link|map|mark|meta|meter|nav|noframes|noscript|object|ol|optgroup|option|output|p|param|pre|progress|q|rp|rt|ruby|samp|script|section|select|small|span|strike|strong|style|sub|sup|table|tbody|td|textarea|tfoot|th|thead|time|title|tr|tt|ul|var|video)\\b",
                r: 0
            }, {
                cN: "pseudo",
                b: ":(visited|valid|root|right|required|read-write|read-only|out-range|optional|only-of-type|only-child|nth-of-type|nth-last-of-type|nth-last-child|nth-child|not|link|left|last-of-type|last-child|lang|invalid|indeterminate|in-range|hover|focus|first-of-type|first-line|first-letter|first-child|first|enabled|empty|disabled|default|checked|before|after|active)"
            }, {
                cN: "pseudo",
                b: "::(after|before|choices|first-letter|first-line|repeat-index|repeat-item|selection|value)"
            }, n, {
                cN: "attribute",
                b: "\\b(z-index|word-wrap|word-spacing|word-break|width|widows|white-space|visibility|vertical-align|unicode-bidi|transition-timing-function|transition-property|transition-duration|transition-delay|transition|transform-style|transform-origin|transform|top|text-underline-position|text-transform|text-shadow|text-rendering|text-overflow|text-indent|text-decoration-style|text-decoration-line|text-decoration-color|text-decoration|text-align-last|text-align|tab-size|table-layout|right|resize|quotes|position|pointer-events|perspective-origin|perspective|page-break-inside|page-break-before|page-break-after|padding-top|padding-right|padding-left|padding-bottom|padding|overflow-y|overflow-x|overflow-wrap|overflow|outline-width|outline-style|outline-offset|outline-color|outline|orphans|order|opacity|object-position|object-fit|normal|none|nav-up|nav-right|nav-left|nav-index|nav-down|min-width|min-height|max-width|max-height|mask|marks|margin-top|margin-right|margin-left|margin-bottom|margin|list-style-type|list-style-position|list-style-image|list-style|line-height|letter-spacing|left|justify-content|initial|inherit|ime-mode|image-orientation|image-resolution|image-rendering|icon|hyphens|height|font-weight|font-variant-ligatures|font-variant|font-style|font-stretch|font-size-adjust|font-size|font-language-override|font-kerning|font-feature-settings|font-family|font|float|flex-wrap|flex-shrink|flex-grow|flex-flow|flex-direction|flex-basis|flex|filter|empty-cells|display|direction|cursor|counter-reset|counter-increment|content|column-width|column-span|column-rule-width|column-rule-style|column-rule-color|column-rule|column-gap|column-fill|column-count|columns|color|clip-path|clip|clear|caption-side|break-inside|break-before|break-after|box-sizing|box-shadow|box-decoration-break|bottom|border-width|border-top-width|border-top-style|border-top-right-radius|border-top-left-radius|border-top-color|border-top|border-style|border-spacing|border-right-width|border-right-style|border-right-color|border-right|border-radius|border-left-width|border-left-style|border-left-color|border-left|border-image-width|border-image-source|border-image-slice|border-image-repeat|border-image-outset|border-image|border-color|border-collapse|border-bottom-width|border-bottom-style|border-bottom-right-radius|border-bottom-left-radius|border-bottom-color|border-bottom|border|background-size|background-repeat|background-position|background-origin|background-image|background-color|background-clip|background-attachment|background-blend-mode|background|backface-visibility|auto|animation-timing-function|animation-play-state|animation-name|animation-iteration-count|animation-fill-mode|animation-duration|animation-direction|animation-delay|animation|align-self|align-items|align-content)\\b",
                i: "[^\\s]"
            }, {
                cN: "value",
                b: "\\b(whitespace|wait|w-resize|visible|vertical-text|vertical-ideographic|uppercase|upper-roman|upper-alpha|underline|transparent|top|thin|thick|text|text-top|text-bottom|tb-rl|table-header-group|table-footer-group|sw-resize|super|strict|static|square|solid|small-caps|separate|se-resize|scroll|s-resize|rtl|row-resize|ridge|right|repeat|repeat-y|repeat-x|relative|progress|pointer|overline|outside|outset|oblique|nowrap|not-allowed|normal|none|nw-resize|no-repeat|no-drop|newspaper|ne-resize|n-resize|move|middle|medium|ltr|lr-tb|lowercase|lower-roman|lower-alpha|loose|list-item|line|line-through|line-edge|lighter|left|keep-all|justify|italic|inter-word|inter-ideograph|inside|inset|inline|inline-block|inherit|inactive|ideograph-space|ideograph-parenthesis|ideograph-numeric|ideograph-alpha|horizontal|hidden|help|hand|groove|fixed|ellipsis|e-resize|double|dotted|distribute|distribute-space|distribute-letter|distribute-all-lines|disc|disabled|default|decimal|dashed|crosshair|collapse|col-resize|circle|char|center|capitalize|break-word|break-all|bottom|both|bolder|bold|block|bidi-override|below|baseline|auto|always|all-scroll|absolute|table|table-cell)\\b"
            }, {
                cN: "value",
                b: ":",
                e: ";",
                c: [r, n, i, t.CSSNM, t.QSM, t.ASM, {
                    cN: "important",
                    b: "!important"
                }]
            }, {
                cN: "at_rule",
                b: "@",
                e: "[{;]",
                k: "mixin include extend for if else each while charset import debug media page content font-face namespace warn",
                c: [r, n, t.QSM, t.ASM, i, t.CSSNM, {
                    cN: "preprocessor",
                    b: "\\s[A-Za-z0-9_.-]+",
                    r: 0
                }]
            }]
        }
    }), + function(t) {
        "use strict";

        function e(e) {
            return this.each(function() {
                var n = t(this),
                    i = n.data("bs.alert");
                i || n.data("bs.alert", i = new r(this)), "string" == typeof e && i[e].call(n)
            })
        }
        var n = '[data-dismiss="alert"]',
            r = function(e) {
                t(e).on("click", n, this.close)
            };
        r.VERSION = "3.2.0", r.prototype.close = function(e) {
            function n() {
                o.detach().trigger("closed.bs.alert").remove()
            }
            var r = t(this),
                i = r.attr("data-target");
            i || (i = r.attr("href"), i = i && i.replace(/.*(?=#[^\s]*$)/, ""));
            var o = t(i);
            e && e.preventDefault(), o.length || (o = r.hasClass("alert") ? r : r.parent()), o.trigger(e = t.Event("close.bs.alert")), e.isDefaultPrevented() || (o.removeClass("in"), t.support.transition && o.hasClass("fade") ? o.one("bsTransitionEnd", n).emulateTransitionEnd(150) : n())
        };
        var i = t.fn.alert;
        t.fn.alert = e, t.fn.alert.Constructor = r, t.fn.alert.noConflict = function() {
            return t.fn.alert = i, this
        }, t(document).on("click.bs.alert.data-api", n, r.prototype.close)
    }(jQuery), "undefined" == typeof jQuery) throw new Error("Bootstrap's JavaScript requires jQuery"); + function(t) {
    "use strict";
    var e = t.fn.jquery.split(" ")[0].split(".");
    if (e[0] < 2 && e[1] < 9 || 1 == e[0] && 9 == e[1] && e[2] < 1) throw new Error("Bootstrap's JavaScript requires jQuery version 1.9.1 or higher")
}(jQuery), + function(t) {
    "use strict";

    function e(e, r) {
        return this.each(function() {
            var i = t(this),
                o = i.data("bs.modal"),
                a = t.extend({}, n.DEFAULTS, i.data(), "object" == typeof e && e);
            o || i.data("bs.modal", o = new n(this, a)), "string" == typeof e ? o[e](r) : a.show && o.show(r)
        })
    }
    var n = function(e, n) {
        this.options = n, this.$body = t(document.body), this.$element = t(e), this.$dialog = this.$element.find(".modal-dialog"), this.$backdrop = null, this.isShown = null, this.originalBodyPad = null, this.scrollbarWidth = 0, this.ignoreBackdropClick = !1, this.options.remote && this.$element.find(".modal-content").load(this.options.remote, t.proxy(function() {
            this.$element.trigger("loaded.bs.modal")
        }, this))
    };
    n.VERSION = "3.3.5", n.TRANSITION_DURATION = 300, n.BACKDROP_TRANSITION_DURATION = 150, n.DEFAULTS = {
        backdrop: !0,
        keyboard: !0,
        show: !0
    }, n.prototype.toggle = function(t) {
        return this.isShown ? this.hide() : this.show(t)
    }, n.prototype.show = function(e) {
        var r = this,
            i = t.Event("show.bs.modal", {
                relatedTarget: e
            });
        this.$element.trigger(i), this.isShown || i.isDefaultPrevented() || (this.isShown = !0, this.checkScrollbar(), this.setScrollbar(), this.$body.addClass("modal-open"), this.escape(), this.resize(), this.$element.on("click.dismiss.bs.modal", '[data-dismiss="modal"]', t.proxy(this.hide, this)), this.$dialog.on("mousedown.dismiss.bs.modal", function() {
            r.$element.one("mouseup.dismiss.bs.modal", function(e) {
                t(e.target).is(r.$element) && (r.ignoreBackdropClick = !0)
            })
        }), this.backdrop(function() {
            var i = t.support.transition && r.$element.hasClass("fade");
            r.$element.parent().length || r.$element.appendTo(r.$body), r.$element.show().scrollTop(0), r.adjustDialog(), i && r.$element[0].offsetWidth, r.$element.addClass("in"), r.enforceFocus();
            var o = t.Event("shown.bs.modal", {
                relatedTarget: e
            });
            i ? r.$dialog.one("bsTransitionEnd", function() {
                r.$element.trigger("focus").trigger(o)
            }).emulateTransitionEnd(n.TRANSITION_DURATION) : r.$element.trigger("focus").trigger(o)
        }))
    }, n.prototype.hide = function(e) {
        e && e.preventDefault(), e = t.Event("hide.bs.modal"), this.$element.trigger(e), this.isShown && !e.isDefaultPrevented() && (this.isShown = !1, this.escape(), this.resize(), t(document).off("focusin.bs.modal"), this.$element.removeClass("in").off("click.dismiss.bs.modal").off("mouseup.dismiss.bs.modal"), this.$dialog.off("mousedown.dismiss.bs.modal"), t.support.transition && this.$element.hasClass("fade") ? this.$element.one("bsTransitionEnd", t.proxy(this.hideModal, this)).emulateTransitionEnd(n.TRANSITION_DURATION) : this.hideModal())
    }, n.prototype.enforceFocus = function() {
        t(document).off("focusin.bs.modal").on("focusin.bs.modal", t.proxy(function(t) {
            this.$element[0] === t.target || this.$element.has(t.target).length || this.$element.trigger("focus")
        }, this))
    }, n.prototype.escape = function() {
        this.isShown && this.options.keyboard ? this.$element.on("keydown.dismiss.bs.modal", t.proxy(function(t) {
            27 == t.which && this.hide()
        }, this)) : this.isShown || this.$element.off("keydown.dismiss.bs.modal")
    }, n.prototype.resize = function() {
        this.isShown ? t(window).on("resize.bs.modal", t.proxy(this.handleUpdate, this)) : t(window).off("resize.bs.modal")
    }, n.prototype.hideModal = function() {
        var t = this;
        this.$element.hide(), this.backdrop(function() {
            t.$body.removeClass("modal-open"), t.resetAdjustments(), t.resetScrollbar(), t.$element.trigger("hidden.bs.modal")
        })
    }, n.prototype.removeBackdrop = function() {
        this.$backdrop && this.$backdrop.remove(), this.$backdrop = null
    }, n.prototype.backdrop = function(e) {
        var r = this,
            i = this.$element.hasClass("fade") ? "fade" : "";
        if (this.isShown && this.options.backdrop) {
            var o = t.support.transition && i;
            if (this.$backdrop = t(document.createElement("div")).addClass("modal-backdrop " + i).appendTo(this.$body), this.$element.on("click.dismiss.bs.modal", t.proxy(function(t) {
                    return this.ignoreBackdropClick ? void(this.ignoreBackdropClick = !1) : void(t.target === t.currentTarget && ("static" == this.options.backdrop ? this.$element[0].focus() : this.hide()))
                }, this)), o && this.$backdrop[0].offsetWidth, this.$backdrop.addClass("in"), !e) return;
            o ? this.$backdrop.one("bsTransitionEnd", e).emulateTransitionEnd(n.BACKDROP_TRANSITION_DURATION) : e()
        } else if (!this.isShown && this.$backdrop) {
            this.$backdrop.removeClass("in");
            var a = function() {
                r.removeBackdrop(), e && e()
            };
            t.support.transition && this.$element.hasClass("fade") ? this.$backdrop.one("bsTransitionEnd", a).emulateTransitionEnd(n.BACKDROP_TRANSITION_DURATION) : a()
        } else e && e()
    }, n.prototype.handleUpdate = function() {
        this.adjustDialog()
    }, n.prototype.adjustDialog = function() {
        var t = this.$element[0].scrollHeight > document.documentElement.clientHeight;
        this.$element.css({
            paddingLeft: !this.bodyIsOverflowing && t ? this.scrollbarWidth : "",
            paddingRight: this.bodyIsOverflowing && !t ? this.scrollbarWidth : ""
        })
    }, n.prototype.resetAdjustments = function() {
        this.$element.css({
            paddingLeft: "",
            paddingRight: ""
        })
    }, n.prototype.checkScrollbar = function() {
        var t = window.innerWidth;
        if (!t) {
            var e = document.documentElement.getBoundingClientRect();
            t = e.right - Math.abs(e.left)
        }
        this.bodyIsOverflowing = document.body.clientWidth < t, this.scrollbarWidth = this.measureScrollbar()
    }, n.prototype.setScrollbar = function() {
        var t = parseInt(this.$body.css("padding-right") || 0, 10);
        this.originalBodyPad = document.body.style.paddingRight || "", this.bodyIsOverflowing && this.$body.css("padding-right", t + this.scrollbarWidth)
    }, n.prototype.resetScrollbar = function() {
        this.$body.css("padding-right", this.originalBodyPad)
    }, n.prototype.measureScrollbar = function() {
        var t = document.createElement("div");
        t.className = "modal-scrollbar-measure", this.$body.append(t);
        var e = t.offsetWidth - t.clientWidth;
        return this.$body[0].removeChild(t), e
    };
    var r = t.fn.modal;
    t.fn.modal = e, t.fn.modal.Constructor = n, t.fn.modal.noConflict = function() {
        return t.fn.modal = r, this
    }, t(document).on("click.bs.modal.data-api", '[data-toggle="modal"]', function(n) {
        var r = t(this),
            i = r.attr("href"),
            o = t(r.attr("data-target") || i && i.replace(/.*(?=#[^\s]+$)/, "")),
            a = o.data("bs.modal") ? "toggle" : t.extend({
                remote: !/#/.test(i) && i
            }, o.data(), r.data());
        r.is("a") && n.preventDefault(), o.one("show.bs.modal", function(t) {
            t.isDefaultPrevented() || o.one("hidden.bs.modal", function() {
                r.is(":visible") && r.trigger("focus")
            })
        }), e.call(o, a, this)
    })
}(jQuery),
function() {
    function t(t, e) {
        if (t !== e) {
            var n = null === t,
                r = t === _,
                i = t === t,
                o = null === e,
                a = e === _,
                s = e === e;
            if (t > e && !o || !i || n && !a && s || r && s) return 1;
            if (e > t && !n || !s || o && !r && i || a && i) return -1
        }
        return 0
    }

    function e(t, e, n) {
        for (var r = t.length, i = n ? r : -1; n ? i-- : ++i < r;)
            if (e(t[i], i, t)) return i;
        return -1
    }

    function n(t, e, n) {
        if (e !== e) return p(t, n);
        for (var r = n - 1, i = t.length; ++r < i;)
            if (t[r] === e) return r;
        return -1
    }

    function r(t) {
        return "function" == typeof t || !1
    }

    function i(t) {
        return null == t ? "" : t + ""
    }

    function o(t, e) {
        for (var n = -1, r = t.length; ++n < r && e.indexOf(t.charAt(n)) > -1;);
        return n
    }

    function a(t, e) {
        for (var n = t.length; n-- && e.indexOf(t.charAt(n)) > -1;);
        return n
    }

    function s(e, n) {
        return t(e.criteria, n.criteria) || e.index - n.index
    }

    function u(e, n, r) {
        for (var i = -1, o = e.criteria, a = n.criteria, s = o.length, u = r.length; ++i < s;) {
            var l = t(o[i], a[i]);
            if (l) {
                if (i >= u) return l;
                var c = r[i];
                return l * ("asc" === c || c === !0 ? 1 : -1)
            }
        }
        return e.index - n.index
    }

    function l(t) {
        return ze[t]
    }

    function c(t) {
        return He[t]
    }

    function f(t, e, n) {
        return e ? t = Ue[t] : n && (t = Ve[t]), "\\" + t
    }

    function d(t) {
        return "\\" + Ve[t]
    }

    function p(t, e, n) {
        for (var r = t.length, i = e + (n ? 0 : -1); n ? i-- : ++i < r;) {
            var o = t[i];
            if (o !== o) return i
        }
        return -1
    }

    function h(t) {
        return !!t && "object" == typeof t
    }

    function g(t) {
        return 160 >= t && t >= 9 && 13 >= t || 32 == t || 160 == t || 5760 == t || 6158 == t || t >= 8192 && (8202 >= t || 8232 == t || 8233 == t || 8239 == t || 8287 == t || 12288 == t || 65279 == t)
    }

    function m(t, e) {
        for (var n = -1, r = t.length, i = -1, o = []; ++n < r;) t[n] === e && (t[n] = z, o[++i] = n);
        return o
    }

    function v(t, e) {
        for (var n, r = -1, i = t.length, o = -1, a = []; ++r < i;) {
            var s = t[r],
                u = e ? e(s, r, t) : s;
            r && n === u || (n = u, a[++o] = s)
        }
        return a
    }

    function y(t) {
        for (var e = -1, n = t.length; ++e < n && g(t.charCodeAt(e)););
        return e
    }

    function b(t) {
        for (var e = t.length; e-- && g(t.charCodeAt(e)););
        return e
    }

    function w(t) {
        return Be[t]
    }

    function x(g) {
        function X(t) {
            if (h(t) && !Nu(t) && !(t instanceof ze)) {
                if (t instanceof te) return t;
                if (es.call(t, "__chain__") && es.call(t, "__wrapped__")) return pi(t)
            }
            return new te(t)
        }

        function Z() {}

        function te(t, e, n) {
            this.__wrapped__ = t, this.__actions__ = n || [], this.__chain__ = !!e
        }

        function ze(t) {
            this.__wrapped__ = t, this.__actions__ = [], this.__dir__ = 1, this.__filtered__ = !1, this.__iteratees__ = [], this.__takeCount__ = Es, this.__views__ = []
        }

        function He() {
            var t = new ze(this.__wrapped__);
            return t.__actions__ = nn(this.__actions__), t.__dir__ = this.__dir__, t.__filtered__ = this.__filtered__, t.__iteratees__ = nn(this.__iteratees__), t.__takeCount__ = this.__takeCount__, t.__views__ = nn(this.__views__), t
        }

        function Be() {
            if (this.__filtered__) {
                var t = new ze(this);
                t.__dir__ = -1, t.__filtered__ = !0
            } else t = this.clone(), t.__dir__ *= -1;
            return t
        }

        function We() {
            var t = this.__wrapped__.value(),
                e = this.__dir__,
                n = Nu(t),
                r = 0 > e,
                i = n ? t.length : 0,
                o = Vr(0, i, this.__views__),
                a = o.start,
                s = o.end,
                u = s - a,
                l = r ? s : a - 1,
                c = this.__iteratees__,
                f = c.length,
                d = 0,
                p = Cs(u, this.__takeCount__);
            if (!n || R > i || i == u && p == u) return rr(t, this.__actions__);
            var h = [];
            t: for (; u-- && p > d;) {
                l += e;
                for (var g = -1, m = t[l]; ++g < f;) {
                    var v = c[g],
                        y = v.iteratee,
                        b = v.type,
                        w = y(m);
                    if (b == M) m = w;
                    else if (!w) {
                        if (b == q) continue t;
                        break t
                    }
                }
                h[d++] = m
            }
            return h
        }

        function Ue() {
            this.__data__ = {}
        }

        function Ve(t) {
            return this.has(t) && delete this.__data__[t]
        }

        function Ke(t) {
            return "__proto__" == t ? _ : this.__data__[t]
        }

        function Xe(t) {
            return "__proto__" != t && es.call(this.__data__, t)
        }

        function Qe(t, e) {
            return "__proto__" != t && (this.__data__[t] = e), this
        }

        function Ge(t) {
            var e = t ? t.length : 0;
            for (this.data = {
                    hash: vs(null),
                    set: new fs
                }; e--;) this.push(t[e])
        }

        function Je(t, e) {
            var n = t.data,
                r = "string" == typeof e || Lo(e) ? n.set.has(e) : n.hash[e];
            return r ? 0 : -1
        }

        function Ze(t) {
            var e = this.data;
            "string" == typeof t || Lo(t) ? e.set.add(t) : e.hash[t] = !0
        }

        function en(t, e) {
            for (var n = -1, r = t.length, i = -1, o = e.length, a = za(r + o); ++n < r;) a[n] = t[n];
            for (; ++i < o;) a[n++] = e[i];
            return a
        }

        function nn(t, e) {
            var n = -1,
                r = t.length;
            for (e || (e = za(r)); ++n < r;) e[n] = t[n];
            return e
        }

        function rn(t, e) {
            for (var n = -1, r = t.length; ++n < r && e(t[n], n, t) !== !1;);
            return t
        }

        function on(t, e) {
            for (var n = t.length; n-- && e(t[n], n, t) !== !1;);
            return t
        }

        function an(t, e) {
            for (var n = -1, r = t.length; ++n < r;)
                if (!e(t[n], n, t)) return !1;
            return !0
        }

        function sn(t, e, n, r) {
            for (var i = -1, o = t.length, a = r, s = a; ++i < o;) {
                var u = t[i],
                    l = +e(u);
                n(l, a) && (a = l, s = u)
            }
            return s
        }

        function un(t, e) {
            for (var n = -1, r = t.length, i = -1, o = []; ++n < r;) {
                var a = t[n];
                e(a, n, t) && (o[++i] = a)
            }
            return o
        }

        function ln(t, e) {
            for (var n = -1, r = t.length, i = za(r); ++n < r;) i[n] = e(t[n], n, t);
            return i
        }

        function cn(t, e) {
            for (var n = -1, r = e.length, i = t.length; ++n < r;) t[i + n] = e[n];
            return t
        }

        function fn(t, e, n, r) {
            var i = -1,
                o = t.length;
            for (r && o && (n = t[++i]); ++i < o;) n = e(n, t[i], i, t);
            return n
        }

        function dn(t, e, n, r) {
            var i = t.length;
            for (r && i && (n = t[--i]); i--;) n = e(n, t[i], i, t);
            return n
        }

        function pn(t, e) {
            for (var n = -1, r = t.length; ++n < r;)
                if (e(t[n], n, t)) return !0;
            return !1
        }

        function hn(t, e) {
            for (var n = t.length, r = 0; n--;) r += +e(t[n]) || 0;
            return r
        }

        function gn(t, e) {
            return t === _ ? e : t
        }

        function mn(t, e, n, r) {
            return t !== _ && es.call(r, n) ? t : e
        }

        function vn(t, e, n) {
            for (var r = -1, i = Pu(e), o = i.length; ++r < o;) {
                var a = i[r],
                    s = t[a],
                    u = n(s, e[a], a, t, e);
                (u === u ? u === s : s !== s) && (s !== _ || a in t) || (t[a] = u)
            }
            return t
        }

        function yn(t, e) {
            return null == e ? t : wn(e, Pu(e), t)
        }

        function bn(t, e) {
            for (var n = -1, r = null == t, i = !r && Jr(t), o = i ? t.length : 0, a = e.length, s = za(a); ++n < a;) {
                var u = e[n];
                s[n] = i ? Zr(u, o) ? t[u] : _ : r ? _ : t[u]
            }
            return s
        }

        function wn(t, e, n) {
            n || (n = {});
            for (var r = -1, i = e.length; ++r < i;) {
                var o = e[r];
                n[o] = t[o]
            }
            return n
        }

        function xn(t, e, n) {
            var r = typeof t;
            return "function" == r ? e === _ ? t : ar(t, e, n) : null == t ? Ea : "object" == r ? Pn(t) : e === _ ? Ia(t) : zn(t, e)
        }

        function _n(t, e, n, r, i, o, a) {
            var s;
            if (n && (s = i ? n(t, r, i) : n(t)), s !== _) return s;
            if (!Lo(t)) return t;
            var u = Nu(t);
            if (u) {
                if (s = Kr(t), !e) return nn(t, s)
            } else {
                var l = rs.call(t),
                    c = l == K;
                if (l != G && l != H && (!c || i)) return Pe[l] ? Qr(t, l, e) : i ? t : {};
                if (s = Xr(c ? {} : t), !e) return yn(s, t)
            }
            o || (o = []), a || (a = []);
            for (var f = o.length; f--;)
                if (o[f] == t) return a[f];
            return o.push(t), a.push(s), (u ? rn : On)(t, function(r, i) {
                s[i] = _n(r, e, n, i, t, o, a)
            }), s
        }

        function Cn(t, e, n) {
            if ("function" != typeof t) throw new Ga(P);
            return ds(function() {
                t.apply(_, n)
            }, e)
        }

        function kn(t, e) {
            var r = t ? t.length : 0,
                i = [];
            if (!r) return i;
            var o = -1,
                a = Br(),
                s = a === n,
                u = s && e.length >= R ? gr(e) : null,
                l = e.length;
            u && (a = Je, s = !1, e = u);
            t: for (; ++o < r;) {
                var c = t[o];
                if (s && c === c) {
                    for (var f = l; f--;)
                        if (e[f] === c) continue t;
                    i.push(c)
                } else a(e, c, 0) < 0 && i.push(c)
            }
            return i
        }

        function Tn(t, e) {
            var n = !0;
            return Fs(t, function(t, r, i) {
                return n = !!e(t, r, i)
            }), n
        }

        function Sn(t, e, n, r) {
            var i = r,
                o = i;
            return Fs(t, function(t, a, s) {
                var u = +e(t, a, s);
                (n(u, i) || u === r && u === o) && (i = u, o = t)
            }), o
        }

        function jn(t, e, n, r) {
            var i = t.length;
            for (n = null == n ? 0 : +n || 0, 0 > n && (n = -n > i ? 0 : i + n), r = r === _ || r > i ? i : +r || 0, 0 > r && (r += i), i = n > r ? 0 : r >>> 0, n >>>= 0; i > n;) t[n++] = e;
            return t
        }

        function En(t, e) {
            var n = [];
            return Fs(t, function(t, r, i) {
                e(t, r, i) && n.push(t)
            }), n
        }

        function Nn(t, e, n, r) {
            var i;
            return n(t, function(t, n, o) {
                return e(t, n, o) ? (i = r ? n : t, !1) : void 0
            }), i
        }

        function An(t, e, n, r) {
            r || (r = []);
            for (var i = -1, o = t.length; ++i < o;) {
                var a = t[i];
                h(a) && Jr(a) && (n || Nu(a) || So(a)) ? e ? An(a, e, n, r) : cn(r, a) : n || (r[r.length] = a)
            }
            return r
        }

        function $n(t, e) {
            return qs(t, e, ea)
        }

        function On(t, e) {
            return qs(t, e, Pu)
        }

        function Dn(t, e) {
            return Ms(t, e, Pu)
        }

        function In(t, e) {
            for (var n = -1, r = e.length, i = -1, o = []; ++n < r;) {
                var a = e[n];
                Io(t[a]) && (o[++i] = a)
            }
            return o
        }

        function Ln(t, e, n) {
            if (null != t) {
                n !== _ && n in fi(t) && (e = [n]);
                for (var r = 0, i = e.length; null != t && i > r;) t = t[e[r++]];
                return r && r == i ? t : _
            }
        }

        function Fn(t, e, n, r, i, o) {
            return t === e ? !0 : null == t || null == e || !Lo(t) && !h(e) ? t !== t && e !== e : Rn(t, e, Fn, n, r, i, o)
        }

        function Rn(t, e, n, r, i, o, a) {
            var s = Nu(t),
                u = Nu(e),
                l = B,
                c = B;
            s || (l = rs.call(t), l == H ? l = G : l != G && (s = Wo(t))), u || (c = rs.call(e), c == H ? c = G : c != G && (u = Wo(e)));
            var f = l == G,
                d = c == G,
                p = l == c;
            if (p && !s && !f) return Mr(t, e, l);
            if (!i) {
                var h = f && es.call(t, "__wrapped__"),
                    g = d && es.call(e, "__wrapped__");
                if (h || g) return n(h ? t.value() : t, g ? e.value() : e, r, i, o, a)
            }
            if (!p) return !1;
            o || (o = []), a || (a = []);
            for (var m = o.length; m--;)
                if (o[m] == t) return a[m] == e;
            o.push(t), a.push(e);
            var v = (s ? qr : Pr)(t, e, n, r, i, o, a);
            return o.pop(), a.pop(), v
        }

        function qn(t, e, n) {
            var r = e.length,
                i = r,
                o = !n;
            if (null == t) return !i;
            for (t = fi(t); r--;) {
                var a = e[r];
                if (o && a[2] ? a[1] !== t[a[0]] : !(a[0] in t)) return !1
            }
            for (; ++r < i;) {
                a = e[r];
                var s = a[0],
                    u = t[s],
                    l = a[1];
                if (o && a[2]) {
                    if (u === _ && !(s in t)) return !1
                } else {
                    var c = n ? n(u, l, s) : _;
                    if (!(c === _ ? Fn(l, u, n, !0) : c)) return !1
                }
            }
            return !0
        }

        function Mn(t, e) {
            var n = -1,
                r = Jr(t) ? za(t.length) : [];
            return Fs(t, function(t, i, o) {
                r[++n] = e(t, i, o)
            }), r
        }

        function Pn(t) {
            var e = Wr(t);
            if (1 == e.length && e[0][2]) {
                var n = e[0][0],
                    r = e[0][1];
                return function(t) {
                    return null == t ? !1 : t[n] === r && (r !== _ || n in fi(t))
                }
            }
            return function(t) {
                return qn(t, e)
            }
        }

        function zn(t, e) {
            var n = Nu(t),
                r = ti(t) && ri(e),
                i = t + "";
            return t = di(t),
                function(o) {
                    if (null == o) return !1;
                    var a = i;
                    if (o = fi(o), !(!n && r || a in o)) {
                        if (o = 1 == t.length ? o : Ln(o, Qn(t, 0, -1)), null == o) return !1;
                        a = Si(t), o = fi(o)
                    }
                    return o[a] === e ? e !== _ || a in o : Fn(e, o[a], _, !0)
                }
        }

        function Hn(t, e, n, r, i) {
            if (!Lo(t)) return t;
            var o = Jr(e) && (Nu(e) || Wo(e)),
                a = o ? _ : Pu(e);
            return rn(a || e, function(s, u) {
                if (a && (u = s, s = e[u]), h(s)) r || (r = []), i || (i = []), Bn(t, e, u, Hn, n, r, i);
                else {
                    var l = t[u],
                        c = n ? n(l, s, u, t, e) : _,
                        f = c === _;
                    f && (c = s), c === _ && (!o || u in t) || !f && (c === c ? c === l : l !== l) || (t[u] = c)
                }
            }), t
        }

        function Bn(t, e, n, r, i, o, a) {
            for (var s = o.length, u = e[n]; s--;)
                if (o[s] == u) return void(t[n] = a[s]);
            var l = t[n],
                c = i ? i(l, u, n, t, e) : _,
                f = c === _;
            f && (c = u, Jr(u) && (Nu(u) || Wo(u)) ? c = Nu(l) ? l : Jr(l) ? nn(l) : [] : zo(u) || So(u) ? c = So(l) ? Qo(l) : zo(l) ? l : {} : f = !1), o.push(u), a.push(c), f ? t[n] = r(c, u, i, o, a) : (c === c ? c !== l : l === l) && (t[n] = c)
        }

        function Wn(t) {
            return function(e) {
                return null == e ? _ : e[t]
            }
        }

        function Un(t) {
            var e = t + "";
            return t = di(t),
                function(n) {
                    return Ln(n, t, e)
                }
        }

        function Vn(t, e) {
            for (var n = t ? e.length : 0; n--;) {
                var r = e[n];
                if (r != i && Zr(r)) {
                    var i = r;
                    ps.call(t, r, 1)
                }
            }
            return t
        }

        function Kn(t, e) {
            return t + ys(Ss() * (e - t + 1))
        }

        function Xn(t, e, n, r, i) {
            return i(t, function(t, i, o) {
                n = r ? (r = !1, t) : e(n, t, i, o)
            }), n
        }

        function Qn(t, e, n) {
            var r = -1,
                i = t.length;
            e = null == e ? 0 : +e || 0, 0 > e && (e = -e > i ? 0 : i + e), n = n === _ || n > i ? i : +n || 0, 0 > n && (n += i), i = e > n ? 0 : n - e >>> 0, e >>>= 0;
            for (var o = za(i); ++r < i;) o[r] = t[r + e];
            return o
        }

        function Gn(t, e) {
            var n;
            return Fs(t, function(t, r, i) {
                return n = e(t, r, i), !n
            }), !!n
        }

        function Jn(t, e) {
            var n = t.length;
            for (t.sort(e); n--;) t[n] = t[n].value;
            return t
        }

        function Zn(t, e, n) {
            var r = zr(),
                i = -1;
            e = ln(e, function(t) {
                return r(t)
            });
            var o = Mn(t, function(t) {
                var n = ln(e, function(e) {
                    return e(t)
                });
                return {
                    criteria: n,
                    index: ++i,
                    value: t
                }
            });
            return Jn(o, function(t, e) {
                return u(t, e, n)
            })
        }

        function Yn(t, e) {
            var n = 0;
            return Fs(t, function(t, r, i) {
                n += +e(t, r, i) || 0
            }), n
        }

        function tr(t, e) {
            var r = -1,
                i = Br(),
                o = t.length,
                a = i === n,
                s = a && o >= R,
                u = s ? gr() : null,
                l = [];
            u ? (i = Je, a = !1) : (s = !1, u = e ? [] : l);
            t: for (; ++r < o;) {
                var c = t[r],
                    f = e ? e(c, r, t) : c;
                if (a && c === c) {
                    for (var d = u.length; d--;)
                        if (u[d] === f) continue t;
                    e && u.push(f), l.push(c)
                } else i(u, f, 0) < 0 && ((e || s) && u.push(f), l.push(c))
            }
            return l
        }

        function er(t, e) {
            for (var n = -1, r = e.length, i = za(r); ++n < r;) i[n] = t[e[n]];
            return i
        }

        function nr(t, e, n, r) {
            for (var i = t.length, o = r ? i : -1;
                (r ? o-- : ++o < i) && e(t[o], o, t););
            return n ? Qn(t, r ? 0 : o, r ? o + 1 : i) : Qn(t, r ? o + 1 : 0, r ? i : o)
        }

        function rr(t, e) {
            var n = t;
            n instanceof ze && (n = n.value());
            for (var r = -1, i = e.length; ++r < i;) {
                var o = e[r];
                n = o.func.apply(o.thisArg, cn([n], o.args))
            }
            return n
        }

        function ir(t, e, n) {
            var r = 0,
                i = t ? t.length : r;
            if ("number" == typeof e && e === e && $s >= i) {
                for (; i > r;) {
                    var o = r + i >>> 1,
                        a = t[o];
                    (n ? e >= a : e > a) && null !== a ? r = o + 1 : i = o
                }
                return i
            }
            return or(t, e, Ea, n)
        }

        function or(t, e, n, r) {
            e = n(e);
            for (var i = 0, o = t ? t.length : 0, a = e !== e, s = null === e, u = e === _; o > i;) {
                var l = ys((i + o) / 2),
                    c = n(t[l]),
                    f = c !== _,
                    d = c === c;
                if (a) var p = d || r;
                else p = s ? d && f && (r || null != c) : u ? d && (r || f) : null == c ? !1 : r ? e >= c : e > c;
                p ? i = l + 1 : o = l
            }
            return Cs(o, As)
        }

        function ar(t, e, n) {
            if ("function" != typeof t) return Ea;
            if (e === _) return t;
            switch (n) {
                case 1:
                    return function(n) {
                        return t.call(e, n)
                    };
                case 3:
                    return function(n, r, i) {
                        return t.call(e, n, r, i)
                    };
                case 4:
                    return function(n, r, i, o) {
                        return t.call(e, n, r, i, o)
                    };
                case 5:
                    return function(n, r, i, o, a) {
                        return t.call(e, n, r, i, o, a)
                    }
            }
            return function() {
                return t.apply(e, arguments)
            }
        }

        function sr(t) {
            var e = new as(t.byteLength),
                n = new hs(e);
            return n.set(new hs(t)), e
        }

        function ur(t, e, n) {
            for (var r = n.length, i = -1, o = _s(t.length - r, 0), a = -1, s = e.length, u = za(s + o); ++a < s;) u[a] = e[a];
            for (; ++i < r;) u[n[i]] = t[i];
            for (; o--;) u[a++] = t[i++];
            return u
        }

        function lr(t, e, n) {
            for (var r = -1, i = n.length, o = -1, a = _s(t.length - i, 0), s = -1, u = e.length, l = za(a + u); ++o < a;) l[o] = t[o];
            for (var c = o; ++s < u;) l[c + s] = e[s];
            for (; ++r < i;) l[c + n[r]] = t[o++];
            return l
        }

        function cr(t, e) {
            return function(n, r, i) {
                var o = e ? e() : {};
                if (r = zr(r, i, 3), Nu(n))
                    for (var a = -1, s = n.length; ++a < s;) {
                        var u = n[a];
                        t(o, u, r(u, a, n), n)
                    } else Fs(n, function(e, n, i) {
                        t(o, e, r(e, n, i), i)
                    });
                return o
            }
        }

        function fr(t) {
            return yo(function(e, n) {
                var r = -1,
                    i = null == e ? 0 : n.length,
                    o = i > 2 ? n[i - 2] : _,
                    a = i > 2 ? n[2] : _,
                    s = i > 1 ? n[i - 1] : _;
                for ("function" == typeof o ? (o = ar(o, s, 5), i -= 2) : (o = "function" == typeof s ? s : _, i -= o ? 1 : 0), a && Yr(n[0], n[1], a) && (o = 3 > i ? _ : o, i = 1); ++r < i;) {
                    var u = n[r];
                    u && t(e, u, o)
                }
                return e
            })
        }

        function dr(t, e) {
            return function(n, r) {
                var i = n ? Hs(n) : 0;
                if (!ni(i)) return t(n, r);
                for (var o = e ? i : -1, a = fi(n);
                    (e ? o-- : ++o < i) && r(a[o], o, a) !== !1;);
                return n
            }
        }

        function pr(t) {
            return function(e, n, r) {
                for (var i = fi(e), o = r(e), a = o.length, s = t ? a : -1; t ? s-- : ++s < a;) {
                    var u = o[s];
                    if (n(i[u], u, i) === !1) break
                }
                return e
            }
        }

        function hr(t, e) {
            function n() {
                var i = this && this !== Ye && this instanceof n ? r : t;
                return i.apply(e, arguments)
            }
            var r = vr(t);
            return n
        }

        function gr(t) {
            return vs && fs ? new Ge(t) : null
        }

        function mr(t) {
            return function(e) {
                for (var n = -1, r = Ta(fa(e)), i = r.length, o = ""; ++n < i;) o = t(o, r[n], n);
                return o
            }
        }

        function vr(t) {
            return function() {
                var e = arguments;
                switch (e.length) {
                    case 0:
                        return new t;
                    case 1:
                        return new t(e[0]);
                    case 2:
                        return new t(e[0], e[1]);
                    case 3:
                        return new t(e[0], e[1], e[2]);
                    case 4:
                        return new t(e[0], e[1], e[2], e[3]);
                    case 5:
                        return new t(e[0], e[1], e[2], e[3], e[4]);
                    case 6:
                        return new t(e[0], e[1], e[2], e[3], e[4], e[5]);
                    case 7:
                        return new t(e[0], e[1], e[2], e[3], e[4], e[5], e[6])
                }
                var n = Ls(t.prototype),
                    r = t.apply(n, e);
                return Lo(r) ? r : n
            }
        }

        function yr(t) {
            function e(n, r, i) {
                i && Yr(n, r, i) && (r = _);
                var o = Rr(n, t, _, _, _, _, _, r);
                return o.placeholder = e.placeholder, o
            }
            return e
        }

        function br(t, e) {
            return yo(function(n) {
                var r = n[0];
                return null == r ? r : (n.push(e), t.apply(_, n))
            })
        }

        function wr(t, e) {
            return function(n, r, i) {
                if (i && Yr(n, r, i) && (r = _), r = zr(r, i, 3), 1 == r.length) {
                    n = Nu(n) ? n : ci(n);
                    var o = sn(n, r, t, e);
                    if (!n.length || o !== e) return o
                }
                return Sn(n, r, t, e)
            }
        }

        function xr(t, n) {
            return function(r, i, o) {
                if (i = zr(i, o, 3), Nu(r)) {
                    var a = e(r, i, n);
                    return a > -1 ? r[a] : _
                }
                return Nn(r, i, t)
            }
        }

        function _r(t) {
            return function(n, r, i) {
                return n && n.length ? (r = zr(r, i, 3), e(n, r, t)) : -1
            }
        }

        function Cr(t) {
            return function(e, n, r) {
                return n = zr(n, r, 3), Nn(e, n, t, !0)
            }
        }

        function kr(t) {
            return function() {
                for (var e, n = arguments.length, r = t ? n : -1, i = 0, o = za(n); t ? r-- : ++r < n;) {
                    var a = o[i++] = arguments[r];
                    if ("function" != typeof a) throw new Ga(P);
                    !e && te.prototype.thru && "wrapper" == Hr(a) && (e = new te([], !0))
                }
                for (r = e ? -1 : n; ++r < n;) {
                    a = o[r];
                    var s = Hr(a),
                        u = "wrapper" == s ? zs(a) : _;
                    e = u && ei(u[0]) && u[1] == ($ | j | N | O) && !u[4].length && 1 == u[9] ? e[Hr(u[0])].apply(e, u[3]) : 1 == a.length && ei(a) ? e[s]() : e.thru(a)
                }
                return function() {
                    var t = arguments,
                        r = t[0];
                    if (e && 1 == t.length && Nu(r) && r.length >= R) return e.plant(r).value();
                    for (var i = 0, a = n ? o[i].apply(this, t) : r; ++i < n;) a = o[i].call(this, a);
                    return a
                }
            }
        }

        function Tr(t, e) {
            return function(n, r, i) {
                return "function" == typeof r && i === _ && Nu(n) ? t(n, r) : e(n, ar(r, i, 3))
            }
        }

        function Sr(t) {
            return function(e, n, r) {
                return ("function" != typeof n || r !== _) && (n = ar(n, r, 3)), t(e, n, ea)
            }
        }

        function jr(t) {
            return function(e, n, r) {
                return ("function" != typeof n || r !== _) && (n = ar(n, r, 3)), t(e, n)
            }
        }

        function Er(t) {
            return function(e, n, r) {
                var i = {};
                return n = zr(n, r, 3), On(e, function(e, r, o) {
                    var a = n(e, r, o);
                    r = t ? a : r, e = t ? e : a, i[r] = e
                }), i
            }
        }

        function Nr(t) {
            return function(e, n, r) {
                return e = i(e), (t ? e : "") + Dr(e, n, r) + (t ? "" : e)
            }
        }

        function Ar(t) {
            var e = yo(function(n, r) {
                var i = m(r, e.placeholder);
                return Rr(n, t, _, r, i)
            });
            return e
        }

        function $r(t, e) {
            return function(n, r, i, o) {
                var a = arguments.length < 3;
                return "function" == typeof r && o === _ && Nu(n) ? t(n, r, i, a) : Xn(n, zr(r, o, 4), i, a, e)
            }
        }

        function Or(t, e, n, r, i, o, a, s, u, l) {
            function c() {
                for (var b = arguments.length, w = b, x = za(b); w--;) x[w] = arguments[w];
                if (r && (x = ur(x, r, i)), o && (x = lr(x, o, a)), h || v) {
                    var C = c.placeholder,
                        S = m(x, C);
                    if (b -= S.length, l > b) {
                        var j = s ? nn(s) : _,
                            E = _s(l - b, 0),
                            $ = h ? S : _,
                            O = h ? _ : S,
                            D = h ? x : _,
                            I = h ? _ : x;
                        e |= h ? N : A, e &= ~(h ? A : N), g || (e &= ~(k | T));
                        var L = [t, e, n, D, $, I, O, j, u, E],
                            F = Or.apply(_, L);
                        return ei(t) && Bs(F, L), F.placeholder = C, F
                    }
                }
                var R = d ? n : this,
                    q = p ? R[t] : t;
                return s && (x = ui(x, s)), f && u < x.length && (x.length = u), this && this !== Ye && this instanceof c && (q = y || vr(t)), q.apply(R, x)
            }
            var f = e & $,
                d = e & k,
                p = e & T,
                h = e & j,
                g = e & S,
                v = e & E,
                y = p ? _ : vr(t);
            return c
        }

        function Dr(t, e, n) {
            var r = t.length;
            if (e = +e, r >= e || !ws(e)) return "";
            var i = e - r;
            return n = null == n ? " " : n + "", va(n, ms(i / n.length)).slice(0, i)
        }

        function Ir(t, e, n, r) {
            function i() {
                for (var e = -1, s = arguments.length, u = -1, l = r.length, c = za(l + s); ++u < l;) c[u] = r[u];
                for (; s--;) c[u++] = arguments[++e];
                var f = this && this !== Ye && this instanceof i ? a : t;
                return f.apply(o ? n : this, c)
            }
            var o = e & k,
                a = vr(t);
            return i
        }

        function Lr(t) {
            var e = Ua[t];
            return function(t, n) {
                return n = n === _ ? 0 : +n || 0, n ? (n = ls(10, n), e(t * n) / n) : e(t)
            }
        }

        function Fr(t) {
            return function(e, n, r, i) {
                var o = zr(r);
                return null == r && o === xn ? ir(e, n, t) : or(e, n, o(r, i, 1), t)
            }
        }

        function Rr(t, e, n, r, i, o, a, s) {
            var u = e & T;
            if (!u && "function" != typeof t) throw new Ga(P);
            var l = r ? r.length : 0;
            if (l || (e &= ~(N | A), r = i = _), l -= i ? i.length : 0, e & A) {
                var c = r,
                    f = i;
                r = i = _
            }
            var d = u ? _ : zs(t),
                p = [t, e, n, r, i, c, f, o, a, s];
            if (d && (ii(p, d), e = p[1], s = p[9]), p[9] = null == s ? u ? 0 : t.length : _s(s - l, 0) || 0, e == k) var h = hr(p[0], p[2]);
            else h = e != N && e != (k | N) || p[4].length ? Or.apply(_, p) : Ir.apply(_, p);
            var g = d ? Ps : Bs;
            return g(h, p)
        }

        function qr(t, e, n, r, i, o, a) {
            var s = -1,
                u = t.length,
                l = e.length;
            if (u != l && !(i && l > u)) return !1;
            for (; ++s < u;) {
                var c = t[s],
                    f = e[s],
                    d = r ? r(i ? f : c, i ? c : f, s) : _;
                if (d !== _) {
                    if (d) continue;
                    return !1
                }
                if (i) {
                    if (!pn(e, function(t) {
                            return c === t || n(c, t, r, i, o, a)
                        })) return !1
                } else if (c !== f && !n(c, f, r, i, o, a)) return !1
            }
            return !0
        }

        function Mr(t, e, n) {
            switch (n) {
                case W:
                case U:
                    return +t == +e;
                case V:
                    return t.name == e.name && t.message == e.message;
                case Q:
                    return t != +t ? e != +e : t == +e;
                case J:
                case Y:
                    return t == e + ""
            }
            return !1
        }

        function Pr(t, e, n, r, i, o, a) {
            var s = Pu(t),
                u = s.length,
                l = Pu(e),
                c = l.length;
            if (u != c && !i) return !1;
            for (var f = u; f--;) {
                var d = s[f];
                if (!(i ? d in e : es.call(e, d))) return !1
            }
            for (var p = i; ++f < u;) {
                d = s[f];
                var h = t[d],
                    g = e[d],
                    m = r ? r(i ? g : h, i ? h : g, d) : _;
                if (!(m === _ ? n(h, g, r, i, o, a) : m)) return !1;
                p || (p = "constructor" == d)
            }
            if (!p) {
                var v = t.constructor,
                    y = e.constructor;
                if (v != y && "constructor" in t && "constructor" in e && !("function" == typeof v && v instanceof v && "function" == typeof y && y instanceof y)) return !1
            }
            return !0
        }

        function zr(t, e, n) {
            var r = X.callback || Sa;
            return r = r === Sa ? xn : r, n ? r(t, e, n) : r
        }

        function Hr(t) {
            for (var e = t.name + "", n = Is[e], r = n ? n.length : 0; r--;) {
                var i = n[r],
                    o = i.func;
                if (null == o || o == t) return i.name
            }
            return e
        }

        function Br(t, e, r) {
            var i = X.indexOf || ki;
            return i = i === ki ? n : i, t ? i(t, e, r) : i
        }

        function Wr(t) {
            for (var e = na(t), n = e.length; n--;) e[n][2] = ri(e[n][1]);
            return e
        }

        function Ur(t, e) {
            var n = null == t ? _ : t[e];
            return qo(n) ? n : _
        }

        function Vr(t, e, n) {
            for (var r = -1, i = n.length; ++r < i;) {
                var o = n[r],
                    a = o.size;
                switch (o.type) {
                    case "drop":
                        t += a;
                        break;
                    case "dropRight":
                        e -= a;
                        break;
                    case "take":
                        e = Cs(e, t + a);
                        break;
                    case "takeRight":
                        t = _s(t, e - a)
                }
            }
            return {
                start: t,
                end: e
            }
        }

        function Kr(t) {
            var e = t.length,
                n = new t.constructor(e);
            return e && "string" == typeof t[0] && es.call(t, "index") && (n.index = t.index, n.input = t.input), n
        }

        function Xr(t) {
            var e = t.constructor;
            return "function" == typeof e && e instanceof e || (e = Ka), new e
        }

        function Qr(t, e, n) {
            var r = t.constructor;
            switch (e) {
                case ee:
                    return sr(t);
                case W:
                case U:
                    return new r(+t);
                case ne:
                case re:
                case ie:
                case oe:
                case ae:
                case se:
                case ue:
                case le:
                case ce:
                    var i = t.buffer;
                    return new r(n ? sr(i) : i, t.byteOffset, t.length);
                case Q:
                case Y:
                    return new r(t);
                case J:
                    var o = new r(t.source, Ne.exec(t));
                    o.lastIndex = t.lastIndex
            }
            return o
        }

        function Gr(t, e, n) {
            null == t || ti(e, t) || (e = di(e), t = 1 == e.length ? t : Ln(t, Qn(e, 0, -1)), e = Si(e));
            var r = null == t ? t : t[e];
            return null == r ? _ : r.apply(t, n)
        }

        function Jr(t) {
            return null != t && ni(Hs(t))
        }

        function Zr(t, e) {
            return t = "number" == typeof t || Oe.test(t) ? +t : -1, e = null == e ? Os : e, t > -1 && t % 1 == 0 && e > t
        }

        function Yr(t, e, n) {
            if (!Lo(n)) return !1;
            var r = typeof e;
            if ("number" == r ? Jr(n) && Zr(e, n.length) : "string" == r && e in n) {
                var i = n[e];
                return t === t ? t === i : i !== i
            }
            return !1
        }

        function ti(t, e) {
            var n = typeof t;
            if ("string" == n && _e.test(t) || "number" == n) return !0;
            if (Nu(t)) return !1;
            var r = !xe.test(t);
            return r || null != e && t in fi(e)
        }

        function ei(t) {
            var e = Hr(t),
                n = X[e];
            if ("function" != typeof n || !(e in ze.prototype)) return !1;
            if (t === n) return !0;
            var r = zs(n);
            return !!r && t === r[0]
        }

        function ni(t) {
            return "number" == typeof t && t > -1 && t % 1 == 0 && Os >= t
        }

        function ri(t) {
            return t === t && !Lo(t)
        }

        function ii(t, e) {
            var n = t[1],
                r = e[1],
                i = n | r,
                o = $ > i,
                a = r == $ && n == j || r == $ && n == O && t[7].length <= e[8] || r == ($ | O) && n == j;
            if (!o && !a) return t;
            r & k && (t[2] = e[2], i |= n & k ? 0 : S);
            var s = e[3];
            if (s) {
                var u = t[3];
                t[3] = u ? ur(u, s, e[4]) : nn(s), t[4] = u ? m(t[3], z) : nn(e[4])
            }
            return s = e[5], s && (u = t[5], t[5] = u ? lr(u, s, e[6]) : nn(s), t[6] = u ? m(t[5], z) : nn(e[6])), s = e[7], s && (t[7] = nn(s)), r & $ && (t[8] = null == t[8] ? e[8] : Cs(t[8], e[8])), null == t[9] && (t[9] = e[9]), t[0] = e[0], t[1] = i, t
        }

        function oi(t, e) {
            return t === _ ? e : Au(t, e, oi)
        }

        function ai(t, e) {
            t = fi(t);
            for (var n = -1, r = e.length, i = {}; ++n < r;) {
                var o = e[n];
                o in t && (i[o] = t[o])
            }
            return i
        }

        function si(t, e) {
            var n = {};
            return $n(t, function(t, r, i) {
                e(t, r, i) && (n[r] = t)
            }), n
        }

        function ui(t, e) {
            for (var n = t.length, r = Cs(e.length, n), i = nn(t); r--;) {
                var o = e[r];
                t[r] = Zr(o, n) ? i[o] : _
            }
            return t
        }

        function li(t) {
            for (var e = ea(t), n = e.length, r = n && t.length, i = !!r && ni(r) && (Nu(t) || So(t)), o = -1, a = []; ++o < n;) {
                var s = e[o];
                (i && Zr(s, r) || es.call(t, s)) && a.push(s)
            }
            return a
        }

        function ci(t) {
            return null == t ? [] : Jr(t) ? Lo(t) ? t : Ka(t) : aa(t)
        }

        function fi(t) {
            return Lo(t) ? t : Ka(t)
        }

        function di(t) {
            if (Nu(t)) return t;
            var e = [];
            return i(t).replace(Ce, function(t, n, r, i) {
                e.push(r ? i.replace(je, "$1") : n || t)
            }), e
        }

        function pi(t) {
            return t instanceof ze ? t.clone() : new te(t.__wrapped__, t.__chain__, nn(t.__actions__))
        }

        function hi(t, e, n) {
            e = (n ? Yr(t, e, n) : null == e) ? 1 : _s(ys(e) || 1, 1);
            for (var r = 0, i = t ? t.length : 0, o = -1, a = za(ms(i / e)); i > r;) a[++o] = Qn(t, r, r += e);
            return a
        }

        function gi(t) {
            for (var e = -1, n = t ? t.length : 0, r = -1, i = []; ++e < n;) {
                var o = t[e];
                o && (i[++r] = o)
            }
            return i
        }

        function mi(t, e, n) {
            var r = t ? t.length : 0;
            return r ? ((n ? Yr(t, e, n) : null == e) && (e = 1), Qn(t, 0 > e ? 0 : e)) : []
        }

        function vi(t, e, n) {
            var r = t ? t.length : 0;
            return r ? ((n ? Yr(t, e, n) : null == e) && (e = 1), e = r - (+e || 0), Qn(t, 0, 0 > e ? 0 : e)) : []
        }

        function yi(t, e, n) {
            return t && t.length ? nr(t, zr(e, n, 3), !0, !0) : []
        }

        function bi(t, e, n) {
            return t && t.length ? nr(t, zr(e, n, 3), !0) : []
        }

        function wi(t, e, n, r) {
            var i = t ? t.length : 0;
            return i ? (n && "number" != typeof n && Yr(t, e, n) && (n = 0, r = i), jn(t, e, n, r)) : []
        }

        function xi(t) {
            return t ? t[0] : _
        }

        function _i(t, e, n) {
            var r = t ? t.length : 0;
            return n && Yr(t, e, n) && (e = !1), r ? An(t, e) : []
        }

        function Ci(t) {
            var e = t ? t.length : 0;
            return e ? An(t, !0) : []
        }

        function ki(t, e, r) {
            var i = t ? t.length : 0;
            if (!i) return -1;
            if ("number" == typeof r) r = 0 > r ? _s(i + r, 0) : r;
            else if (r) {
                var o = ir(t, e);
                return i > o && (e === e ? e === t[o] : t[o] !== t[o]) ? o : -1
            }
            return n(t, e, r || 0)
        }

        function Ti(t) {
            return vi(t, 1)
        }

        function Si(t) {
            var e = t ? t.length : 0;
            return e ? t[e - 1] : _
        }

        function ji(t, e, n) {
            var r = t ? t.length : 0;
            if (!r) return -1;
            var i = r;
            if ("number" == typeof n) i = (0 > n ? _s(r + n, 0) : Cs(n || 0, r - 1)) + 1;
            else if (n) {
                i = ir(t, e, !0) - 1;
                var o = t[i];
                return (e === e ? e === o : o !== o) ? i : -1
            }
            if (e !== e) return p(t, i, !0);
            for (; i--;)
                if (t[i] === e) return i;
            return -1
        }

        function Ei() {
            var t = arguments,
                e = t[0];
            if (!e || !e.length) return e;
            for (var n = 0, r = Br(), i = t.length; ++n < i;)
                for (var o = 0, a = t[n];
                    (o = r(e, a, o)) > -1;) ps.call(e, o, 1);
            return e
        }

        function Ni(t, e, n) {
            var r = [];
            if (!t || !t.length) return r;
            var i = -1,
                o = [],
                a = t.length;
            for (e = zr(e, n, 3); ++i < a;) {
                var s = t[i];
                e(s, i, t) && (r.push(s), o.push(i))
            }
            return Vn(t, o), r
        }

        function Ai(t) {
            return mi(t, 1)
        }

        function $i(t, e, n) {
            var r = t ? t.length : 0;
            return r ? (n && "number" != typeof n && Yr(t, e, n) && (e = 0, n = r), Qn(t, e, n)) : []
        }

        function Oi(t, e, n) {
            var r = t ? t.length : 0;
            return r ? ((n ? Yr(t, e, n) : null == e) && (e = 1), Qn(t, 0, 0 > e ? 0 : e)) : []
        }

        function Di(t, e, n) {
            var r = t ? t.length : 0;
            return r ? ((n ? Yr(t, e, n) : null == e) && (e = 1), e = r - (+e || 0), Qn(t, 0 > e ? 0 : e)) : []
        }

        function Ii(t, e, n) {
            return t && t.length ? nr(t, zr(e, n, 3), !1, !0) : []
        }

        function Li(t, e, n) {
            return t && t.length ? nr(t, zr(e, n, 3)) : []
        }

        function Fi(t, e, r, i) {
            var o = t ? t.length : 0;
            if (!o) return [];
            null != e && "boolean" != typeof e && (i = r, r = Yr(t, e, i) ? _ : e, e = !1);
            var a = zr();
            return (null != r || a !== xn) && (r = a(r, i, 3)), e && Br() === n ? v(t, r) : tr(t, r)
        }

        function Ri(t) {
            if (!t || !t.length) return [];
            var e = -1,
                n = 0;
            t = un(t, function(t) {
                return Jr(t) ? (n = _s(t.length, n), !0) : void 0
            });
            for (var r = za(n); ++e < n;) r[e] = ln(t, Wn(e));
            return r
        }

        function qi(t, e, n) {
            var r = t ? t.length : 0;
            if (!r) return [];
            var i = Ri(t);
            return null == e ? i : (e = ar(e, n, 4), ln(i, function(t) {
                return fn(t, e, _, !0)
            }))
        }

        function Mi() {
            for (var t = -1, e = arguments.length; ++t < e;) {
                var n = arguments[t];
                if (Jr(n)) var r = r ? cn(kn(r, n), kn(n, r)) : n
            }
            return r ? tr(r) : []
        }

        function Pi(t, e) {
            var n = -1,
                r = t ? t.length : 0,
                i = {};
            for (!r || e || Nu(t[0]) || (e = []); ++n < r;) {
                var o = t[n];
                e ? i[o] = e[n] : o && (i[o[0]] = o[1])
            }
            return i
        }

        function zi(t) {
            var e = X(t);
            return e.__chain__ = !0, e
        }

        function Hi(t, e, n) {
            return e.call(n, t), t
        }

        function Bi(t, e, n) {
            return e.call(n, t)
        }

        function Wi() {
            return zi(this)
        }

        function Ui() {
            return new te(this.value(), this.__chain__)
        }

        function Vi(t) {
            for (var e, n = this; n instanceof Z;) {
                var r = pi(n);
                e ? i.__wrapped__ = r : e = r;
                var i = r;
                n = n.__wrapped__
            }
            return i.__wrapped__ = t, e
        }

        function Ki() {
            var t = this.__wrapped__,
                e = function(t) {
                    return t.reverse()
                };
            if (t instanceof ze) {
                var n = t;
                return this.__actions__.length && (n = new ze(this)), n = n.reverse(), n.__actions__.push({
                    func: Bi,
                    args: [e],
                    thisArg: _
                }), new te(n, this.__chain__)
            }
            return this.thru(e)
        }

        function Xi() {
            return this.value() + ""
        }

        function Qi() {
            return rr(this.__wrapped__, this.__actions__)
        }

        function Gi(t, e, n) {
            var r = Nu(t) ? an : Tn;
            return n && Yr(t, e, n) && (e = _), ("function" != typeof e || n !== _) && (e = zr(e, n, 3)), r(t, e)
        }

        function Ji(t, e, n) {
            var r = Nu(t) ? un : En;
            return e = zr(e, n, 3), r(t, e)
        }

        function Zi(t, e) {
            return iu(t, Pn(e))
        }

        function Yi(t, e, n, r) {
            var i = t ? Hs(t) : 0;
            return ni(i) || (t = aa(t), i = t.length), n = "number" != typeof n || r && Yr(e, n, r) ? 0 : 0 > n ? _s(i + n, 0) : n || 0, "string" == typeof t || !Nu(t) && Bo(t) ? i >= n && t.indexOf(e, n) > -1 : !!i && Br(t, e, n) > -1
        }

        function to(t, e, n) {
            var r = Nu(t) ? ln : Mn;
            return e = zr(e, n, 3), r(t, e)
        }

        function eo(t, e) {
            return to(t, Ia(e))
        }

        function no(t, e, n) {
            var r = Nu(t) ? un : En;
            return e = zr(e, n, 3), r(t, function(t, n, r) {
                return !e(t, n, r)
            })
        }

        function ro(t, e, n) {
            if (n ? Yr(t, e, n) : null == e) {
                t = ci(t);
                var r = t.length;
                return r > 0 ? t[Kn(0, r - 1)] : _
            }
            var i = -1,
                o = Xo(t),
                r = o.length,
                a = r - 1;
            for (e = Cs(0 > e ? 0 : +e || 0, r); ++i < e;) {
                var s = Kn(i, a),
                    u = o[s];
                o[s] = o[i], o[i] = u
            }
            return o.length = e, o
        }

        function io(t) {
            return ro(t, Es)
        }

        function oo(t) {
            var e = t ? Hs(t) : 0;
            return ni(e) ? e : Pu(t).length
        }

        function ao(t, e, n) {
            var r = Nu(t) ? pn : Gn;
            return n && Yr(t, e, n) && (e = _), ("function" != typeof e || n !== _) && (e = zr(e, n, 3)), r(t, e)
        }

        function so(t, e, n) {
            if (null == t) return [];
            n && Yr(t, e, n) && (e = _);
            var r = -1;
            e = zr(e, n, 3);
            var i = Mn(t, function(t, n, i) {
                return {
                    criteria: e(t, n, i),
                    index: ++r,
                    value: t
                }
            });
            return Jn(i, s)
        }

        function uo(t, e, n, r) {
            return null == t ? [] : (r && Yr(e, n, r) && (n = _), Nu(e) || (e = null == e ? [] : [e]), Nu(n) || (n = null == n ? [] : [n]), Zn(t, e, n))
        }

        function lo(t, e) {
            return Ji(t, Pn(e))
        }

        function co(t, e) {
            if ("function" != typeof e) {
                if ("function" != typeof t) throw new Ga(P);
                var n = t;
                t = e, e = n
            }
            return t = ws(t = +t) ? t : 0,
                function() {
                    return --t < 1 ? e.apply(this, arguments) : void 0
                }
        }

        function fo(t, e, n) {
            return n && Yr(t, e, n) && (e = _), e = t && null == e ? t.length : _s(+e || 0, 0), Rr(t, $, _, _, _, _, e)
        }

        function po(t, e) {
            var n;
            if ("function" != typeof e) {
                if ("function" != typeof t) throw new Ga(P);
                var r = t;
                t = e, e = r
            }
            return function() {
                return --t > 0 && (n = e.apply(this, arguments)), 1 >= t && (e = _), n
            }
        }

        function ho(t, e, n) {
            function r() {
                p && ss(p), l && ss(l), g = 0, l = p = h = _
            }

            function i(e, n) {
                n && ss(n), l = p = h = _, e && (g = gu(), c = t.apply(d, u), p || l || (u = d = _))
            }

            function o() {
                var t = e - (gu() - f);
                0 >= t || t > e ? i(h, l) : p = ds(o, t)
            }

            function a() {
                i(v, p)
            }

            function s() {
                if (u = arguments, f = gu(), d = this, h = v && (p || !y), m === !1) var n = y && !p;
                else {
                    l || y || (g = f);
                    var r = m - (f - g),
                        i = 0 >= r || r > m;
                    i ? (l && (l = ss(l)), g = f, c = t.apply(d, u)) : l || (l = ds(a, r))
                }
                return i && p ? p = ss(p) : p || e === m || (p = ds(o, e)), n && (i = !0, c = t.apply(d, u)), !i || p || l || (u = d = _), c
            }
            var u, l, c, f, d, p, h, g = 0,
                m = !1,
                v = !0;
            if ("function" != typeof t) throw new Ga(P);
            if (e = 0 > e ? 0 : +e || 0, n === !0) {
                var y = !0;
                v = !1
            } else Lo(n) && (y = !!n.leading, m = "maxWait" in n && _s(+n.maxWait || 0, e), v = "trailing" in n ? !!n.trailing : v);
            return s.cancel = r, s
        }

        function go(t, e) {
            if ("function" != typeof t || e && "function" != typeof e) throw new Ga(P);
            var n = function() {
                var r = arguments,
                    i = e ? e.apply(this, r) : r[0],
                    o = n.cache;
                if (o.has(i)) return o.get(i);
                var a = t.apply(this, r);
                return n.cache = o.set(i, a), a
            };
            return n.cache = new go.Cache, n
        }

        function mo(t) {
            if ("function" != typeof t) throw new Ga(P);
            return function() {
                return !t.apply(this, arguments)
            }
        }

        function vo(t) {
            return po(2, t)
        }

        function yo(t, e) {
            if ("function" != typeof t) throw new Ga(P);
            return e = _s(e === _ ? t.length - 1 : +e || 0, 0),
                function() {
                    for (var n = arguments, r = -1, i = _s(n.length - e, 0), o = za(i); ++r < i;) o[r] = n[e + r];
                    switch (e) {
                        case 0:
                            return t.call(this, o);
                        case 1:
                            return t.call(this, n[0], o);
                        case 2:
                            return t.call(this, n[0], n[1], o)
                    }
                    var a = za(e + 1);
                    for (r = -1; ++r < e;) a[r] = n[r];
                    return a[e] = o, t.apply(this, a)
                }
        }

        function bo(t) {
            if ("function" != typeof t) throw new Ga(P);
            return function(e) {
                return t.apply(this, e)
            }
        }

        function wo(t, e, n) {
            var r = !0,
                i = !0;
            if ("function" != typeof t) throw new Ga(P);
            return n === !1 ? r = !1 : Lo(n) && (r = "leading" in n ? !!n.leading : r, i = "trailing" in n ? !!n.trailing : i), ho(t, e, {
                leading: r,
                maxWait: +e,
                trailing: i
            })
        }

        function xo(t, e) {
            return e = null == e ? Ea : e, Rr(e, N, _, [t], [])
        }

        function _o(t, e, n, r) {
            return e && "boolean" != typeof e && Yr(t, e, n) ? e = !1 : "function" == typeof e && (r = n, n = e, e = !1), "function" == typeof n ? _n(t, e, ar(n, r, 3)) : _n(t, e)
        }

        function Co(t, e, n) {
            return "function" == typeof e ? _n(t, !0, ar(e, n, 3)) : _n(t, !0)
        }

        function ko(t, e) {
            return t > e
        }

        function To(t, e) {
            return t >= e
        }

        function So(t) {
            return h(t) && Jr(t) && es.call(t, "callee") && !cs.call(t, "callee")
        }

        function jo(t) {
            return t === !0 || t === !1 || h(t) && rs.call(t) == W
        }

        function Eo(t) {
            return h(t) && rs.call(t) == U
        }

        function No(t) {
            return !!t && 1 === t.nodeType && h(t) && !zo(t)
        }

        function Ao(t) {
            return null == t ? !0 : Jr(t) && (Nu(t) || Bo(t) || So(t) || h(t) && Io(t.splice)) ? !t.length : !Pu(t).length
        }

        function $o(t, e, n, r) {
            n = "function" == typeof n ? ar(n, r, 3) : _;
            var i = n ? n(t, e) : _;
            return i === _ ? Fn(t, e, n) : !!i
        }

        function Oo(t) {
            return h(t) && "string" == typeof t.message && rs.call(t) == V
        }

        function Do(t) {
            return "number" == typeof t && ws(t)
        }

        function Io(t) {
            return Lo(t) && rs.call(t) == K
        }

        function Lo(t) {
            var e = typeof t;
            return !!t && ("object" == e || "function" == e)
        }

        function Fo(t, e, n, r) {
            return n = "function" == typeof n ? ar(n, r, 3) : _, qn(t, Wr(e), n)
        }

        function Ro(t) {
            return Po(t) && t != +t
        }

        function qo(t) {
            return null == t ? !1 : Io(t) ? os.test(ts.call(t)) : h(t) && $e.test(t)
        }

        function Mo(t) {
            return null === t
        }

        function Po(t) {
            return "number" == typeof t || h(t) && rs.call(t) == Q
        }

        function zo(t) {
            var e;
            if (!h(t) || rs.call(t) != G || So(t) || !es.call(t, "constructor") && (e = t.constructor, "function" == typeof e && !(e instanceof e))) return !1;
            var n;
            return $n(t, function(t, e) {
                n = e
            }), n === _ || es.call(t, n)
        }

        function Ho(t) {
            return Lo(t) && rs.call(t) == J
        }

        function Bo(t) {
            return "string" == typeof t || h(t) && rs.call(t) == Y
        }

        function Wo(t) {
            return h(t) && ni(t.length) && !!Me[rs.call(t)]
        }

        function Uo(t) {
            return t === _
        }

        function Vo(t, e) {
            return e > t
        }

        function Ko(t, e) {
            return e >= t
        }

        function Xo(t) {
            var e = t ? Hs(t) : 0;
            return ni(e) ? e ? nn(t) : [] : aa(t)
        }

        function Qo(t) {
            return wn(t, ea(t))
        }

        function Go(t, e, n) {
            var r = Ls(t);
            return n && Yr(t, e, n) && (e = _), e ? yn(r, e) : r
        }

        function Jo(t) {
            return In(t, ea(t))
        }

        function Zo(t, e, n) {
            var r = null == t ? _ : Ln(t, di(e), e + "");
            return r === _ ? n : r
        }

        function Yo(t, e) {
            if (null == t) return !1;
            var n = es.call(t, e);
            if (!n && !ti(e)) {
                if (e = di(e), t = 1 == e.length ? t : Ln(t, Qn(e, 0, -1)), null == t) return !1;
                e = Si(e), n = es.call(t, e)
            }
            return n || ni(t.length) && Zr(e, t.length) && (Nu(t) || So(t))
        }

        function ta(t, e, n) {
            n && Yr(t, e, n) && (e = _);
            for (var r = -1, i = Pu(t), o = i.length, a = {}; ++r < o;) {
                var s = i[r],
                    u = t[s];
                e ? es.call(a, u) ? a[u].push(s) : a[u] = [s] : a[u] = s
            }
            return a
        }

        function ea(t) {
            if (null == t) return [];
            Lo(t) || (t = Ka(t));
            var e = t.length;
            e = e && ni(e) && (Nu(t) || So(t)) && e || 0;
            for (var n = t.constructor, r = -1, i = "function" == typeof n && n.prototype === t, o = za(e), a = e > 0; ++r < e;) o[r] = r + "";
            for (var s in t) a && Zr(s, e) || "constructor" == s && (i || !es.call(t, s)) || o.push(s);
            return o
        }

        function na(t) {
            t = fi(t);
            for (var e = -1, n = Pu(t), r = n.length, i = za(r); ++e < r;) {
                var o = n[e];
                i[e] = [o, t[o]]
            }
            return i
        }

        function ra(t, e, n) {
            var r = null == t ? _ : t[e];
            return r === _ && (null == t || ti(e, t) || (e = di(e), t = 1 == e.length ? t : Ln(t, Qn(e, 0, -1)), r = null == t ? _ : t[Si(e)]), r = r === _ ? n : r), Io(r) ? r.call(t) : r
        }

        function ia(t, e, n) {
            if (null == t) return t;
            var r = e + "";
            e = null != t[r] || ti(e, t) ? [r] : di(e);
            for (var i = -1, o = e.length, a = o - 1, s = t; null != s && ++i < o;) {
                var u = e[i];
                Lo(s) && (i == a ? s[u] = n : null == s[u] && (s[u] = Zr(e[i + 1]) ? [] : {})), s = s[u]
            }
            return t
        }

        function oa(t, e, n, r) {
            var i = Nu(t) || Wo(t);
            if (e = zr(e, r, 4), null == n)
                if (i || Lo(t)) {
                    var o = t.constructor;
                    n = i ? Nu(t) ? new o : [] : Ls(Io(o) ? o.prototype : _)
                } else n = {};
            return (i ? rn : On)(t, function(t, r, i) {
                return e(n, t, r, i)
            }), n
        }

        function aa(t) {
            return er(t, Pu(t))
        }

        function sa(t) {
            return er(t, ea(t))
        }

        function ua(t, e, n) {
            return e = +e || 0, n === _ ? (n = e, e = 0) : n = +n || 0, t >= Cs(e, n) && t < _s(e, n)
        }

        function la(t, e, n) {
            n && Yr(t, e, n) && (e = n = _);
            var r = null == t,
                i = null == e;
            if (null == n && (i && "boolean" == typeof t ? (n = t, t = 1) : "boolean" == typeof e && (n = e, i = !0)), r && i && (e = 1, i = !1), t = +t || 0, i ? (e = t, t = 0) : e = +e || 0, n || t % 1 || e % 1) {
                var o = Ss();
                return Cs(t + o * (e - t + us("1e-" + ((o + "").length - 1))), e)
            }
            return Kn(t, e)
        }

        function ca(t) {
            return t = i(t), t && t.charAt(0).toUpperCase() + t.slice(1)
        }

        function fa(t) {
            return t = i(t), t && t.replace(De, l).replace(Se, "")
        }

        function da(t, e, n) {
            t = i(t), e += "";
            var r = t.length;
            return n = n === _ ? r : Cs(0 > n ? 0 : +n || 0, r), n -= e.length, n >= 0 && t.indexOf(e, n) == n
        }

        function pa(t) {
            return t = i(t), t && ve.test(t) ? t.replace(ge, c) : t
        }

        function ha(t) {
            return t = i(t), t && Te.test(t) ? t.replace(ke, f) : t || "(?:)"
        }

        function ga(t, e, n) {
            t = i(t), e = +e;
            var r = t.length;
            if (r >= e || !ws(e)) return t;
            var o = (e - r) / 2,
                a = ys(o),
                s = ms(o);
            return n = Dr("", s, n), n.slice(0, a) + t + n
        }

        function ma(t, e, n) {
            return (n ? Yr(t, e, n) : null == e) ? e = 0 : e && (e = +e), t = wa(t), Ts(t, e || (Ae.test(t) ? 16 : 10))
        }

        function va(t, e) {
            var n = "";
            if (t = i(t), e = +e, 1 > e || !t || !ws(e)) return n;
            do e % 2 && (n += t), e = ys(e / 2), t += t; while (e);
            return n
        }

        function ya(t, e, n) {
            return t = i(t), n = null == n ? 0 : Cs(0 > n ? 0 : +n || 0, t.length), t.lastIndexOf(e, n) == n
        }

        function ba(t, e, n) {
            var r = X.templateSettings;
            n && Yr(t, e, n) && (e = n = _), t = i(t), e = vn(yn({}, n || e), r, mn);
            var o, a, s = vn(yn({}, e.imports), r.imports, mn),
                u = Pu(s),
                l = er(s, u),
                c = 0,
                f = e.interpolate || Ie,
                p = "__p += '",
                h = Xa((e.escape || Ie).source + "|" + f.source + "|" + (f === we ? Ee : Ie).source + "|" + (e.evaluate || Ie).source + "|$", "g"),
                g = "//# sourceURL=" + ("sourceURL" in e ? e.sourceURL : "lodash.templateSources[" + ++qe + "]") + "\n";
            t.replace(h, function(e, n, r, i, s, u) {
                return r || (r = i), p += t.slice(c, u).replace(Le, d), n && (o = !0, p += "' +\n__e(" + n + ") +\n'"), s && (a = !0, p += "';\n" + s + ";\n__p += '"), r && (p += "' +\n((__t = (" + r + ")) == null ? '' : __t) +\n'"), c = u + e.length, e
            }), p += "';\n";
            var m = e.variable;
            m || (p = "with (obj) {\n" + p + "\n}\n"), p = (a ? p.replace(fe, "") : p).replace(de, "$1").replace(pe, "$1;"), p = "function(" + (m || "obj") + ") {\n" + (m ? "" : "obj || (obj = {});\n") + "var __t, __p = ''" + (o ? ", __e = _.escape" : "") + (a ? ", __j = Array.prototype.join;\nfunction print() { __p += __j.call(arguments, '') }\n" : ";\n") + p + "return __p\n}";
            var v = Ju(function() {
                return Wa(u, g + "return " + p).apply(_, l)
            });
            if (v.source = p, Oo(v)) throw v;
            return v
        }

        function wa(t, e, n) {
            var r = t;
            return (t = i(t)) ? (n ? Yr(r, e, n) : null == e) ? t.slice(y(t), b(t) + 1) : (e += "", t.slice(o(t, e), a(t, e) + 1)) : t
        }

        function xa(t, e, n) {
            var r = t;
            return t = i(t), t ? t.slice((n ? Yr(r, e, n) : null == e) ? y(t) : o(t, e + "")) : t
        }

        function _a(t, e, n) {
            var r = t;
            return t = i(t), t ? (n ? Yr(r, e, n) : null == e) ? t.slice(0, b(t) + 1) : t.slice(0, a(t, e + "") + 1) : t
        }

        function Ca(t, e, n) {
            n && Yr(t, e, n) && (e = _);
            var r = D,
                o = I;
            if (null != e)
                if (Lo(e)) {
                    var a = "separator" in e ? e.separator : a;
                    r = "length" in e ? +e.length || 0 : r, o = "omission" in e ? i(e.omission) : o
                } else r = +e || 0;
            if (t = i(t), r >= t.length) return t;
            var s = r - o.length;
            if (1 > s) return o;
            var u = t.slice(0, s);
            if (null == a) return u + o;
            if (Ho(a)) {
                if (t.slice(s).search(a)) {
                    var l, c, f = t.slice(0, s);
                    for (a.global || (a = Xa(a.source, (Ne.exec(a) || "") + "g")), a.lastIndex = 0; l = a.exec(f);) c = l.index;
                    u = u.slice(0, null == c ? s : c)
                }
            } else if (t.indexOf(a, s) != s) {
                var d = u.lastIndexOf(a);
                d > -1 && (u = u.slice(0, d))
            }
            return u + o
        }

        function ka(t) {
            return t = i(t), t && me.test(t) ? t.replace(he, w) : t
        }

        function Ta(t, e, n) {
            return n && Yr(t, e, n) && (e = _), t = i(t), t.match(e || Fe) || []
        }

        function Sa(t, e, n) {
            return n && Yr(t, e, n) && (e = _), h(t) ? Na(t) : xn(t, e)
        }

        function ja(t) {
            return function() {
                return t
            }
        }

        function Ea(t) {
            return t
        }

        function Na(t) {
            return Pn(_n(t, !0))
        }

        function Aa(t, e) {
            return zn(t, _n(e, !0))
        }

        function $a(t, e, n) {
            if (null == n) {
                var r = Lo(e),
                    i = r ? Pu(e) : _,
                    o = i && i.length ? In(e, i) : _;
                (o ? o.length : r) || (o = !1, n = e, e = t, t = this)
            }
            o || (o = In(e, Pu(e)));
            var a = !0,
                s = -1,
                u = Io(t),
                l = o.length;
            n === !1 ? a = !1 : Lo(n) && "chain" in n && (a = n.chain);
            for (; ++s < l;) {
                var c = o[s],
                    f = e[c];
                t[c] = f, u && (t.prototype[c] = function(e) {
                    return function() {
                        var n = this.__chain__;
                        if (a || n) {
                            var r = t(this.__wrapped__),
                                i = r.__actions__ = nn(this.__actions__);
                            return i.push({
                                func: e,
                                args: arguments,
                                thisArg: t
                            }), r.__chain__ = n, r
                        }
                        return e.apply(t, cn([this.value()], arguments))
                    }
                }(f))
            }
            return t
        }

        function Oa() {
            return Ye._ = is, this
        }

        function Da() {}

        function Ia(t) {
            return ti(t) ? Wn(t) : Un(t)
        }

        function La(t) {
            return function(e) {
                return Ln(t, di(e), e + "")
            }
        }

        function Fa(t, e, n) {
            n && Yr(t, e, n) && (e = n = _), t = +t || 0, n = null == n ? 1 : +n || 0, null == e ? (e = t, t = 0) : e = +e || 0;
            for (var r = -1, i = _s(ms((e - t) / (n || 1)), 0), o = za(i); ++r < i;) o[r] = t, t += n;
            return o
        }

        function Ra(t, e, n) {
            if (t = ys(t), 1 > t || !ws(t)) return [];
            var r = -1,
                i = za(Cs(t, Ns));
            for (e = ar(e, n, 1); ++r < t;) Ns > r ? i[r] = e(r) : e(r);
            return i
        }

        function qa(t) {
            var e = ++ns;
            return i(t) + e
        }

        function Ma(t, e) {
            return (+t || 0) + (+e || 0)
        }

        function Pa(t, e, n) {
            return n && Yr(t, e, n) && (e = _), e = zr(e, n, 3), 1 == e.length ? hn(Nu(t) ? t : ci(t), e) : Yn(t, e)
        }
        g = g ? tn.defaults(Ye.Object(), g, tn.pick(Ye, Re)) : Ye; {
            var za = g.Array,
                Ha = g.Date,
                Ba = g.Error,
                Wa = g.Function,
                Ua = g.Math,
                Va = g.Number,
                Ka = g.Object,
                Xa = g.RegExp,
                Qa = g.String,
                Ga = g.TypeError,
                Ja = za.prototype,
                Za = Ka.prototype,
                Ya = Qa.prototype,
                ts = Wa.prototype.toString,
                es = Za.hasOwnProperty,
                ns = 0,
                rs = Za.toString,
                is = Ye._,
                os = Xa("^" + ts.call(es).replace(/[\\^$.*+?()[\]{}|]/g, "\\$&").replace(/hasOwnProperty|(function).*?(?=\\\()| for .+?(?=\\\])/g, "$1.*?") + "$"),
                as = g.ArrayBuffer,
                ss = g.clearTimeout,
                us = g.parseFloat,
                ls = Ua.pow,
                cs = Za.propertyIsEnumerable,
                fs = Ur(g, "Set"),
                ds = g.setTimeout,
                ps = Ja.splice,
                hs = g.Uint8Array,
                gs = Ur(g, "WeakMap"),
                ms = Ua.ceil,
                vs = Ur(Ka, "create"),
                ys = Ua.floor,
                bs = Ur(za, "isArray"),
                ws = g.isFinite,
                xs = Ur(Ka, "keys"),
                _s = Ua.max,
                Cs = Ua.min,
                ks = Ur(Ha, "now"),
                Ts = g.parseInt,
                Ss = Ua.random,
                js = Va.NEGATIVE_INFINITY,
                Es = Va.POSITIVE_INFINITY,
                Ns = 4294967295,
                As = Ns - 1,
                $s = Ns >>> 1,
                Os = 9007199254740991,
                Ds = gs && new gs,
                Is = {};
            X.support = {}
        }
        X.templateSettings = {
            escape: ye,
            evaluate: be,
            interpolate: we,
            variable: "",
            imports: {
                _: X
            }
        };
        var Ls = function() {
                function t() {}
                return function(e) {
                    if (Lo(e)) {
                        t.prototype = e;
                        var n = new t;
                        t.prototype = _
                    }
                    return n || {}
                }
            }(),
            Fs = dr(On),
            Rs = dr(Dn, !0),
            qs = pr(),
            Ms = pr(!0),
            Ps = Ds ? function(t, e) {
                return Ds.set(t, e), t
            } : Ea,
            zs = Ds ? function(t) {
                return Ds.get(t)
            } : Da,
            Hs = Wn("length"),
            Bs = function() {
                var t = 0,
                    e = 0;
                return function(n, r) {
                    var i = gu(),
                        o = F - (i - e);
                    if (e = i, o > 0) {
                        if (++t >= L) return n
                    } else t = 0;
                    return Ps(n, r)
                }
            }(),
            Ws = yo(function(t, e) {
                return h(t) && Jr(t) ? kn(t, An(e, !1, !0)) : []
            }),
            Us = _r(),
            Vs = _r(!0),
            Ks = yo(function(t) {
                for (var e = t.length, r = e, i = za(f), o = Br(), a = o === n, s = []; r--;) {
                    var u = t[r] = Jr(u = t[r]) ? u : [];
                    i[r] = a && u.length >= 120 ? gr(r && u) : null
                }
                var l = t[0],
                    c = -1,
                    f = l ? l.length : 0,
                    d = i[0];
                t: for (; ++c < f;)
                    if (u = l[c], (d ? Je(d, u) : o(s, u, 0)) < 0) {
                        for (var r = e; --r;) {
                            var p = i[r];
                            if ((p ? Je(p, u) : o(t[r], u, 0)) < 0) continue t
                        }
                        d && d.push(u), s.push(u)
                    }
                return s
            }),
            Xs = yo(function(e, n) {
                n = An(n);
                var r = bn(e, n);
                return Vn(e, n.sort(t)), r
            }),
            Qs = Fr(),
            Gs = Fr(!0),
            Js = yo(function(t) {
                return tr(An(t, !1, !0))
            }),
            Zs = yo(function(t, e) {
                return Jr(t) ? kn(t, e) : []
            }),
            Ys = yo(Ri),
            tu = yo(function(t) {
                var e = t.length,
                    n = e > 2 ? t[e - 2] : _,
                    r = e > 1 ? t[e - 1] : _;
                return e > 2 && "function" == typeof n ? e -= 2 : (n = e > 1 && "function" == typeof r ? (--e, r) : _, r = _), t.length = e, qi(t, n, r)
            }),
            eu = yo(function(t) {
                return t = An(t), this.thru(function(e) {
                    return en(Nu(e) ? e : [fi(e)], t)
                })
            }),
            nu = yo(function(t, e) {
                return bn(t, An(e))
            }),
            ru = cr(function(t, e, n) {
                es.call(t, n) ? ++t[n] : t[n] = 1
            }),
            iu = xr(Fs),
            ou = xr(Rs, !0),
            au = Tr(rn, Fs),
            su = Tr(on, Rs),
            uu = cr(function(t, e, n) {
                es.call(t, n) ? t[n].push(e) : t[n] = [e]
            }),
            lu = cr(function(t, e, n) {
                t[n] = e
            }),
            cu = yo(function(t, e, n) {
                var r = -1,
                    i = "function" == typeof e,
                    o = ti(e),
                    a = Jr(t) ? za(t.length) : [];
                return Fs(t, function(t) {
                    var s = i ? e : o && null != t ? t[e] : _;
                    a[++r] = s ? s.apply(t, n) : Gr(t, e, n)
                }), a
            }),
            fu = cr(function(t, e, n) {
                t[n ? 0 : 1].push(e)
            }, function() {
                return [
                    [],
                    []
                ]
            }),
            du = $r(fn, Fs),
            pu = $r(dn, Rs),
            hu = yo(function(t, e) {
                if (null == t) return [];
                var n = e[2];
                return n && Yr(e[0], e[1], n) && (e.length = 1), Zn(t, An(e), [])
            }),
            gu = ks || function() {
                return (new Ha).getTime()
            },
            mu = yo(function(t, e, n) {
                var r = k;
                if (n.length) {
                    var i = m(n, mu.placeholder);
                    r |= N
                }
                return Rr(t, r, e, n, i)
            }),
            vu = yo(function(t, e) {
                e = e.length ? An(e) : Jo(t);
                for (var n = -1, r = e.length; ++n < r;) {
                    var i = e[n];
                    t[i] = Rr(t[i], k, t)
                }
                return t
            }),
            yu = yo(function(t, e, n) {
                var r = k | T;
                if (n.length) {
                    var i = m(n, yu.placeholder);
                    r |= N
                }
                return Rr(e, r, t, n, i)
            }),
            bu = yr(j),
            wu = yr(E),
            xu = yo(function(t, e) {
                return Cn(t, 1, e)
            }),
            _u = yo(function(t, e, n) {
                return Cn(t, e, n)
            }),
            Cu = kr(),
            ku = kr(!0),
            Tu = yo(function(t, e) {
                if (e = An(e), "function" != typeof t || !an(e, r)) throw new Ga(P);
                var n = e.length;
                return yo(function(r) {
                    for (var i = Cs(r.length, n); i--;) r[i] = e[i](r[i]);
                    return t.apply(this, r)
                })
            }),
            Su = Ar(N),
            ju = Ar(A),
            Eu = yo(function(t, e) {
                return Rr(t, O, _, _, _, An(e))
            }),
            Nu = bs || function(t) {
                return h(t) && ni(t.length) && rs.call(t) == B
            },
            Au = fr(Hn),
            $u = fr(function(t, e, n) {
                return n ? vn(t, e, n) : yn(t, e)
            }),
            Ou = br($u, gn),
            Du = br(Au, oi),
            Iu = Cr(On),
            Lu = Cr(Dn),
            Fu = Sr(qs),
            Ru = Sr(Ms),
            qu = jr(On),
            Mu = jr(Dn),
            Pu = xs ? function(t) {
                var e = null == t ? _ : t.constructor;
                return "function" == typeof e && e.prototype === t || "function" != typeof t && Jr(t) ? li(t) : Lo(t) ? xs(t) : []
            } : li,
            zu = Er(!0),
            Hu = Er(),
            Bu = yo(function(t, e) {
                if (null == t) return {};
                if ("function" != typeof e[0]) {
                    var e = ln(An(e), Qa);
                    return ai(t, kn(ea(t), e))
                }
                var n = ar(e[0], e[1], 3);
                return si(t, function(t, e, r) {
                    return !n(t, e, r)
                })
            }),
            Wu = yo(function(t, e) {
                return null == t ? {} : "function" == typeof e[0] ? si(t, ar(e[0], e[1], 3)) : ai(t, An(e))
            }),
            Uu = mr(function(t, e, n) {
                return e = e.toLowerCase(), t + (n ? e.charAt(0).toUpperCase() + e.slice(1) : e)
            }),
            Vu = mr(function(t, e, n) {
                return t + (n ? "-" : "") + e.toLowerCase()
            }),
            Ku = Nr(),
            Xu = Nr(!0),
            Qu = mr(function(t, e, n) {
                return t + (n ? "_" : "") + e.toLowerCase()
            }),
            Gu = mr(function(t, e, n) {
                return t + (n ? " " : "") + (e.charAt(0).toUpperCase() + e.slice(1))
            }),
            Ju = yo(function(t, e) {
                try {
                    return t.apply(_, e)
                } catch (n) {
                    return Oo(n) ? n : new Ba(n)
                }
            }),
            Zu = yo(function(t, e) {
                return function(n) {
                    return Gr(n, t, e)
                }
            }),
            Yu = yo(function(t, e) {
                return function(n) {
                    return Gr(t, n, e)
                }
            }),
            tl = Lr("ceil"),
            el = Lr("floor"),
            nl = wr(ko, js),
            rl = wr(Vo, Es),
            il = Lr("round");
        return X.prototype = Z.prototype, te.prototype = Ls(Z.prototype), te.prototype.constructor = te, ze.prototype = Ls(Z.prototype), ze.prototype.constructor = ze, Ue.prototype["delete"] = Ve, Ue.prototype.get = Ke, Ue.prototype.has = Xe, Ue.prototype.set = Qe, Ge.prototype.push = Ze, go.Cache = Ue, X.after = co, X.ary = fo, X.assign = $u, X.at = nu, X.before = po, X.bind = mu, X.bindAll = vu, X.bindKey = yu, X.callback = Sa, X.chain = zi, X.chunk = hi, X.compact = gi, X.constant = ja, X.countBy = ru, X.create = Go, X.curry = bu, X.curryRight = wu, X.debounce = ho, X.defaults = Ou, X.defaultsDeep = Du, X.defer = xu, X.delay = _u, X.difference = Ws, X.drop = mi, X.dropRight = vi, X.dropRightWhile = yi, X.dropWhile = bi, X.fill = wi, X.filter = Ji, X.flatten = _i, X.flattenDeep = Ci, X.flow = Cu, X.flowRight = ku, X.forEach = au, X.forEachRight = su, X.forIn = Fu, X.forInRight = Ru, X.forOwn = qu, X.forOwnRight = Mu, X.functions = Jo, X.groupBy = uu, X.indexBy = lu, X.initial = Ti, X.intersection = Ks, X.invert = ta, X.invoke = cu, X.keys = Pu, X.keysIn = ea, X.map = to, X.mapKeys = zu, X.mapValues = Hu, X.matches = Na, X.matchesProperty = Aa, X.memoize = go, X.merge = Au, X.method = Zu, X.methodOf = Yu, X.mixin = $a, X.modArgs = Tu, X.negate = mo, X.omit = Bu, X.once = vo, X.pairs = na, X.partial = Su, X.partialRight = ju, X.partition = fu, X.pick = Wu, X.pluck = eo, X.property = Ia, X.propertyOf = La, X.pull = Ei, X.pullAt = Xs, X.range = Fa, X.rearg = Eu, X.reject = no, X.remove = Ni, X.rest = Ai, X.restParam = yo, X.set = ia, X.shuffle = io, X.slice = $i, X.sortBy = so, X.sortByAll = hu, X.sortByOrder = uo, X.spread = bo, X.take = Oi, X.takeRight = Di, X.takeRightWhile = Ii, X.takeWhile = Li, X.tap = Hi, X.throttle = wo, X.thru = Bi, X.times = Ra, X.toArray = Xo, X.toPlainObject = Qo, X.transform = oa, X.union = Js, X.uniq = Fi, X.unzip = Ri, X.unzipWith = qi, X.values = aa, X.valuesIn = sa, X.where = lo, X.without = Zs, X.wrap = xo, X.xor = Mi, X.zip = Ys, X.zipObject = Pi, X.zipWith = tu, X.backflow = ku, X.collect = to, X.compose = ku, X.each = au, X.eachRight = su, X.extend = $u, X.iteratee = Sa, X.methods = Jo, X.object = Pi, X.select = Ji, X.tail = Ai, X.unique = Fi, $a(X, X), X.add = Ma, X.attempt = Ju, X.camelCase = Uu, X.capitalize = ca, X.ceil = tl, X.clone = _o, X.cloneDeep = Co, X.deburr = fa, X.endsWith = da, X.escape = pa, X.escapeRegExp = ha, X.every = Gi, X.find = iu, X.findIndex = Us, X.findKey = Iu, X.findLast = ou, X.findLastIndex = Vs, X.findLastKey = Lu, X.findWhere = Zi, X.first = xi, X.floor = el, X.get = Zo, X.gt = ko, X.gte = To, X.has = Yo, X.identity = Ea, X.includes = Yi, X.indexOf = ki, X.inRange = ua, X.isArguments = So, X.isArray = Nu, X.isBoolean = jo, X.isDate = Eo, X.isElement = No, X.isEmpty = Ao, X.isEqual = $o, X.isError = Oo, X.isFinite = Do, X.isFunction = Io, X.isMatch = Fo, X.isNaN = Ro, X.isNative = qo, X.isNull = Mo, X.isNumber = Po, X.isObject = Lo, X.isPlainObject = zo, X.isRegExp = Ho, X.isString = Bo, X.isTypedArray = Wo, X.isUndefined = Uo, X.kebabCase = Vu, X.last = Si, X.lastIndexOf = ji, X.lt = Vo, X.lte = Ko, X.max = nl, X.min = rl, X.noConflict = Oa, X.noop = Da, X.now = gu, X.pad = ga, X.padLeft = Ku, X.padRight = Xu, X.parseInt = ma, X.random = la, X.reduce = du, X.reduceRight = pu, X.repeat = va, X.result = ra, X.round = il, X.runInContext = x, X.size = oo, X.snakeCase = Qu, X.some = ao, X.sortedIndex = Qs, X.sortedLastIndex = Gs, X.startCase = Gu, X.startsWith = ya, X.sum = Pa, X.template = ba, X.trim = wa, X.trimLeft = xa, X.trimRight = _a, X.trunc = Ca, X.unescape = ka, X.uniqueId = qa, X.words = Ta, X.all = Gi, X.any = ao, X.contains = Yi, X.eq = $o, X.detect = iu, X.foldl = du, X.foldr = pu, X.head = xi, X.include = Yi, X.inject = du, $a(X, function() {
            var t = {};
            return On(X, function(e, n) {
                X.prototype[n] || (t[n] = e)
            }), t
        }(), !1), X.sample = ro, X.prototype.sample = function(t) {
            return this.__chain__ || null != t ? this.thru(function(e) {
                return ro(e, t)
            }) : ro(this.value())
        }, X.VERSION = C, rn(["bind", "bindKey", "curry", "curryRight", "partial", "partialRight"], function(t) {
            X[t].placeholder = X
        }), rn(["drop", "take"], function(t, e) {
            ze.prototype[t] = function(n) {
                var r = this.__filtered__;
                if (r && !e) return new ze(this);
                n = null == n ? 1 : _s(ys(n) || 0, 0);
                var i = this.clone();
                return r ? i.__takeCount__ = Cs(i.__takeCount__, n) : i.__views__.push({
                    size: n,
                    type: t + (i.__dir__ < 0 ? "Right" : "")
                }), i
            }, ze.prototype[t + "Right"] = function(e) {
                return this.reverse()[t](e).reverse()
            }
        }), rn(["filter", "map", "takeWhile"], function(t, e) {
            var n = e + 1,
                r = n != M;
            ze.prototype[t] = function(t, e) {
                var i = this.clone();
                return i.__iteratees__.push({
                    iteratee: zr(t, e, 1),
                    type: n
                }), i.__filtered__ = i.__filtered__ || r, i
            }
        }), rn(["first", "last"], function(t, e) {
            var n = "take" + (e ? "Right" : "");
            ze.prototype[t] = function() {
                return this[n](1).value()[0]
            }
        }), rn(["initial", "rest"], function(t, e) {
            var n = "drop" + (e ? "" : "Right");
            ze.prototype[t] = function() {
                return this.__filtered__ ? new ze(this) : this[n](1)
            }
        }), rn(["pluck", "where"], function(t, e) {
            var n = e ? "filter" : "map",
                r = e ? Pn : Ia;
            ze.prototype[t] = function(t) {
                return this[n](r(t))
            }
        }), ze.prototype.compact = function() {
            return this.filter(Ea)
        }, ze.prototype.reject = function(t, e) {
            return t = zr(t, e, 1), this.filter(function(e) {
                return !t(e)
            })
        }, ze.prototype.slice = function(t, e) {
            t = null == t ? 0 : +t || 0;
            var n = this;
            return n.__filtered__ && (t > 0 || 0 > e) ? new ze(n) : (0 > t ? n = n.takeRight(-t) : t && (n = n.drop(t)), e !== _ && (e = +e || 0, n = 0 > e ? n.dropRight(-e) : n.take(e - t)), n)
        }, ze.prototype.takeRightWhile = function(t, e) {
            return this.reverse().takeWhile(t, e).reverse()
        }, ze.prototype.toArray = function() {
            return this.take(Es)
        }, On(ze.prototype, function(t, e) {
            var n = /^(?:filter|map|reject)|While$/.test(e),
                r = /^(?:first|last)$/.test(e),
                i = X[r ? "take" + ("last" == e ? "Right" : "") : e];
            i && (X.prototype[e] = function() {
                var e = r ? [1] : arguments,
                    o = this.__chain__,
                    a = this.__wrapped__,
                    s = !!this.__actions__.length,
                    u = a instanceof ze,
                    l = e[0],
                    c = u || Nu(a);
                c && n && "function" == typeof l && 1 != l.length && (u = c = !1);
                var f = function(t) {
                        return r && o ? i(t, 1)[0] : i.apply(_, cn([t], e))
                    },
                    d = {
                        func: Bi,
                        args: [f],
                        thisArg: _
                    },
                    p = u && !s;
                if (r && !o) return p ? (a = a.clone(), a.__actions__.push(d), t.call(a)) : i.call(_, this.value())[0];
                if (!r && c) {
                    a = p ? a : new ze(this);
                    var h = t.apply(a, e);
                    return h.__actions__.push(d), new te(h, o)
                }
                return this.thru(f)
            })
        }), rn(["join", "pop", "push", "replace", "shift", "sort", "splice", "split", "unshift"], function(t) {
            var e = (/^(?:replace|split)$/.test(t) ? Ya : Ja)[t],
                n = /^(?:push|sort|unshift)$/.test(t) ? "tap" : "thru",
                r = /^(?:join|pop|replace|shift)$/.test(t);
            X.prototype[t] = function() {
                var t = arguments;
                return r && !this.__chain__ ? e.apply(this.value(), t) : this[n](function(n) {
                    return e.apply(n, t)
                })
            }
        }), On(ze.prototype, function(t, e) {
            var n = X[e];
            if (n) {
                var r = n.name + "",
                    i = Is[r] || (Is[r] = []);
                i.push({
                    name: e,
                    func: n
                })
            }
        }), Is[Or(_, T).name] = [{
            name: "wrapper",
            func: _
        }], ze.prototype.clone = He, ze.prototype.reverse = Be, ze.prototype.value = We, X.prototype.chain = Wi, X.prototype.commit = Ui, X.prototype.concat = eu, X.prototype.plant = Vi, X.prototype.reverse = Ki, X.prototype.toString = Xi, X.prototype.run = X.prototype.toJSON = X.prototype.valueOf = X.prototype.value = Qi, X.prototype.collect = X.prototype.map, X.prototype.head = X.prototype.first, X.prototype.select = X.prototype.filter, X.prototype.tail = X.prototype.rest, X
    }
    var _, C = "3.10.1",
        k = 1,
        T = 2,
        S = 4,
        j = 8,
        E = 16,
        N = 32,
        A = 64,
        $ = 128,
        O = 256,
        D = 30,
        I = "...",
        L = 150,
        F = 16,
        R = 200,
        q = 1,
        M = 2,
        P = "Expected a function",
        z = "__lodash_placeholder__",
        H = "[object Arguments]",
        B = "[object Array]",
        W = "[object Boolean]",
        U = "[object Date]",
        V = "[object Error]",
        K = "[object Function]",
        X = "[object Map]",
        Q = "[object Number]",
        G = "[object Object]",
        J = "[object RegExp]",
        Z = "[object Set]",
        Y = "[object String]",
        te = "[object WeakMap]",
        ee = "[object ArrayBuffer]",
        ne = "[object Float32Array]",
        re = "[object Float64Array]",
        ie = "[object Int8Array]",
        oe = "[object Int16Array]",
        ae = "[object Int32Array]",
        se = "[object Uint8Array]",
        ue = "[object Uint8ClampedArray]",
        le = "[object Uint16Array]",
        ce = "[object Uint32Array]",
        fe = /\b__p \+= '';/g,
        de = /\b(__p \+=) '' \+/g,
        pe = /(__e\(.*?\)|\b__t\)) \+\n'';/g,
        he = /&(?:amp|lt|gt|quot|#39|#96);/g,
        ge = /[&<>"'`]/g,
        me = RegExp(he.source),
        ve = RegExp(ge.source),
        ye = /<%-([\s\S]+?)%>/g,
        be = /<%([\s\S]+?)%>/g,
        we = /<%=([\s\S]+?)%>/g,
        xe = /\.|\[(?:[^[\]]*|(["'])(?:(?!\1)[^\n\\]|\\.)*?\1)\]/,
        _e = /^\w*$/,
        Ce = /[^.[\]]+|\[(?:(-?\d+(?:\.\d+)?)|(["'])((?:(?!\2)[^\n\\]|\\.)*?)\2)\]/g,
        ke = /^[:!,]|[\\^$.*+?()[\]{}|\/]|(^[0-9a-fA-Fnrtuvx])|([\n\r\u2028\u2029])/g,
        Te = RegExp(ke.source),
        Se = /[\u0300-\u036f\ufe20-\ufe23]/g,
        je = /\\(\\)?/g,
        Ee = /\$\{([^\\}]*(?:\\.[^\\}]*)*)\}/g,
        Ne = /\w*$/,
        Ae = /^0[xX]/,
        $e = /^\[object .+?Constructor\]$/,
        Oe = /^\d+$/,
        De = /[\xc0-\xd6\xd8-\xde\xdf-\xf6\xf8-\xff]/g,
        Ie = /($^)/,
        Le = /['\n\r\u2028\u2029\\]/g,
        Fe = function() {
            var t = "[A-Z\\xc0-\\xd6\\xd8-\\xde]",
                e = "[a-z\\xdf-\\xf6\\xf8-\\xff]+";
            return RegExp(t + "+(?=" + t + e + ")|" + t + "?" + e + "|" + t + "+|[0-9]+", "g")
        }(),
        Re = ["Array", "ArrayBuffer", "Date", "Error", "Float32Array", "Float64Array", "Function", "Int8Array", "Int16Array", "Int32Array", "Math", "Number", "Object", "RegExp", "Set", "String", "_", "clearTimeout", "isFinite", "parseFloat", "parseInt", "setTimeout", "TypeError", "Uint8Array", "Uint8ClampedArray", "Uint16Array", "Uint32Array", "WeakMap"],
        qe = -1,
        Me = {};
    Me[ne] = Me[re] = Me[ie] = Me[oe] = Me[ae] = Me[se] = Me[ue] = Me[le] = Me[ce] = !0, Me[H] = Me[B] = Me[ee] = Me[W] = Me[U] = Me[V] = Me[K] = Me[X] = Me[Q] = Me[G] = Me[J] = Me[Z] = Me[Y] = Me[te] = !1;
    var Pe = {};
    Pe[H] = Pe[B] = Pe[ee] = Pe[W] = Pe[U] = Pe[ne] = Pe[re] = Pe[ie] = Pe[oe] = Pe[ae] = Pe[Q] = Pe[G] = Pe[J] = Pe[Y] = Pe[se] = Pe[ue] = Pe[le] = Pe[ce] = !0, Pe[V] = Pe[K] = Pe[X] = Pe[Z] = Pe[te] = !1;
    var ze = {
            "\xc0": "A",
            "\xc1": "A",
            "\xc2": "A",
            "\xc3": "A",
            "\xc4": "A",
            "\xc5": "A",
            "\xe0": "a",
            "\xe1": "a",
            "\xe2": "a",
            "\xe3": "a",
            "\xe4": "a",
            "\xe5": "a",
            "\xc7": "C",
            "\xe7": "c",
            "\xd0": "D",
            "\xf0": "d",
            "\xc8": "E",
            "\xc9": "E",
            "\xca": "E",
            "\xcb": "E",
            "\xe8": "e",
            "\xe9": "e",
            "\xea": "e",
            "\xeb": "e",
            "\xcc": "I",
            "\xcd": "I",
            "\xce": "I",
            "\xcf": "I",
            "\xec": "i",
            "\xed": "i",
            "\xee": "i",
            "\xef": "i",
            "\xd1": "N",
            "\xf1": "n",
            "\xd2": "O",
            "\xd3": "O",
            "\xd4": "O",
            "\xd5": "O",
            "\xd6": "O",
            "\xd8": "O",
            "\xf2": "o",
            "\xf3": "o",
            "\xf4": "o",
            "\xf5": "o",
            "\xf6": "o",
            "\xf8": "o",
            "\xd9": "U",
            "\xda": "U",
            "\xdb": "U",
            "\xdc": "U",
            "\xf9": "u",
            "\xfa": "u",
            "\xfb": "u",
            "\xfc": "u",
            "\xdd": "Y",
            "\xfd": "y",
            "\xff": "y",
            "\xc6": "Ae",
            "\xe6": "ae",
            "\xde": "Th",
            "\xfe": "th",
            "\xdf": "ss"
        },
        He = {
            "&": "&amp;",
            "<": "&lt;",
            ">": "&gt;",
            '"': "&quot;",
            "'": "&#39;",
            "`": "&#96;"
        },
        Be = {
            "&amp;": "&",
            "&lt;": "<",
            "&gt;": ">",
            "&quot;": '"',
            "&#39;": "'",
            "&#96;": "`"
        },
        We = {
            "function": !0,
            object: !0
        },
        Ue = {
            0: "x30",
            1: "x31",
            2: "x32",
            3: "x33",
            4: "x34",
            5: "x35",
            6: "x36",
            7: "x37",
            8: "x38",
            9: "x39",
            A: "x41",
            B: "x42",
            C: "x43",
            D: "x44",
            E: "x45",
            F: "x46",
            a: "x61",
            b: "x62",
            c: "x63",
            d: "x64",
            e: "x65",
            f: "x66",
            n: "x6e",
            r: "x72",
            t: "x74",
            u: "x75",
            v: "x76",
            x: "x78"
        },
        Ve = {
            "\\": "\\",
            "'": "'",
            "\n": "n",
            "\r": "r",
            "\u2028": "u2028",
            "\u2029": "u2029"
        },
        Ke = We[typeof exports] && exports && !exports.nodeType && exports,
        Xe = We[typeof module] && module && !module.nodeType && module,
        Qe = Ke && Xe && "object" == typeof global && global && global.Object && global,
        Ge = We[typeof self] && self && self.Object && self,
        Je = We[typeof window] && window && window.Object && window,
        Ze = Xe && Xe.exports === Ke && Ke,
        Ye = Qe || Je !== (this && this.window) && Je || Ge || this,
        tn = x();
    "function" == typeof define && "object" == typeof define.amd && define.amd ? (Ye._ = tn, define(function() {
        return tn
    })) : Ke && Xe ? Ze ? (Xe.exports = tn)._ = tn : Ke._ = tn : Ye._ = tn
}.call(this), $(".admin_firms.edit,.admin_logos.edit").ready(function() {
    $(".firm-name").qtip({
        content: {
            text: "If you require a change to your firm name, please contact our support team."
        },
        position: {
            my: "center left",
            at: "center right",
            adjust: {
                x: -55,
                y: 0
            }
        },
        style: "qtip-light"
    }), $(".firm-crd").qtip({
        content: {
            text: "If you require a change to your firm's CRD, please contact our support team."
        },
        position: {
            my: "center left",
            at: "center right",
            adjust: {
                x: -40,
                y: 0
            }
        },
        style: "qtip-light"
    }), $("#firmLogoExamples").qtip({
        content: {
            text: function() {
                return $.parseHTML('<div class="firm-logo">Color logo example with a transparent background</div><img class="color-logo" src="https://betterment-institutional-public-demo.s3.amazonaws.com/assets/example_color_firm_logo-107e15c536632cbcc9b841367cfa47ff.png"/><div class="firm-logo">White logo example with a transparent background</div><img class="white-logo" src="https://betterment-institutional-public-demo.s3.amazonaws.com/assets/example_white_firm_logo-e0c3f3d92f1388bb3781660e82e5efda.png"/>')
            }
        },
        show: "mousedown",
        hide: {
            event: "mousedown unfocus"
        },
        style: {
            classes: "qtip-light firm-logo-examples-tooltip"
        },
        position: {
            my: "top center",
            at: "bottom center",
            adjust: {
                y: 20
            }
        }
    })
});
var BMT = BMT || {};
! function() {
    $(document).on("click", "[data-track-event]", function(t) {
        var e = $(t.currentTarget).data();
        if (e) {
            var n = e.trackEvent;
            if (n) {
                var r = {},
                    i = e.trackLocation;
                i && (r.Location = i);
                var o = e.trackName;
                o && (r.Name = o);
                var a = e.trackModule;
                a && (r.Module = a);
                var s = e.trackType;
                s && (r.Type = s);
                var u = e.trackAdvisorId;
                u && (r.AdvisorID = u), r.Path = window.location.pathname;
                try {
                    mixpanel.track(n, r)
                } catch (t) {}
            }
        }
    }), BMT.Analytics = {
        init: function() {
            mixpanel.register_once({
                Actor: "Advisor",
                App: "Institutional",
                Platform: "Web"
            })
        }
    }
}(), $(".client_invites.index").ready(function() {
    $("#invite_link_link").click(function() {
        $(this).select()
    })
}), $(".composites.index, .compliance_composites.index").ready(function() {
    var t = function(t) {
            $.pjax({
                url: n(),
                container: "#dashboard"
            }).success(function() {
                t && t()
            })
        },
        e = _.debounce(t, 250),
        n = function() {
            var t = $(".composite-search input").val(),
                e = $("#compositeGroupingSelect").val();
            return "?search=" + encodeURIComponent(t) + "&filter=" + encodeURIComponent(e)
        },
        r = $(".composites-panel");
    r.pjax("a[data-pjax]", "#dashboard"), r.on("pjax:start", function() {
        r.find(".loading").show()
    }), r.on("pjax:success", function() {
        r.find(".loading").hide()
    }), r.on("keyup search", ".composite-search input", function() {
        var t = $(this);
        e(function() {
            t.focus()
        })
    }), $("#compositeGroupingSelect").selectize({
        onChange: function() {
            t()
        }
    })
}), $(".composites").ready(function() {
    var t = function(t) {
            $.pjax({
                url: e(t),
                container: "#clientAccounts"
            })
        },
        e = function(t) {
            var e = $("#clientAccounts").data("url");
            return e + "?client_id=" + encodeURIComponent(t)
        };
    $("#clientDropdown").selectize({
        selectOnTab: !0,
        onChange: t
    });
    var n = $("#edit_composite_name");
    n.find("input[type=text]").on("blur", function() {
        n.submit()
    }), $(".composite-name").on("click", function() {
        n.addClass("active"), $(this).removeClass("active")
    })
}), $(document).ready(function() {
    $(".pricing-plan a").on("ajax:before", function() {
        var t = $(this).parents(".composite-account-group-panel").find(".fee-override-container");
        return t.is(":empty") ? !0 : (t.html(""), !1)
    }), $("body").on("ajax:before", "form.new_allocation_change", function() {
        Spinner.show("form.new_allocation_change")
    }), $("body").on("ajax:error", "form.new_allocation_change", function() {
        Spinner.hide("form.new_allocation_change")
    }), $(".allocation-change-link").on("ajax:before", function() {
        Spinner.show(".composites-show")
    }), $(".allocation-change-link").on("ajax:complete", function() {
        Spinner.hide(".composites-show")
    })
}), $(document).on("ajax:error", function() {
    $("#errorModal").modal("show")
}), $(".firms_registrations.new, .firms_registrations.create").ready(function() {
    $(".advisor-spread-bps").qtip({
        content: {
            text: "Spread your firm will charge on top of the 25bps platform fee."
        },
        position: {
            my: "top right",
            at: "bottom right",
            adjust: {
                x: 0,
                y: 0
            }
        },
        style: "qtip-light"
    }), $("#firmLogoExamples").qtip({
        content: {
            text: function() {
                return $.parseHTML('<div class="firm-logo">Color logo example with a transparent background</div><img class="color-logo" src="https://betterment-institutional-public-demo.s3.amazonaws.com/assets/example_color_firm_logo-107e15c536632cbcc9b841367cfa47ff.png"/><div class="firm-logo">White logo example with a transparent background</div><img class="white-logo" src="https://betterment-institutional-public-demo.s3.amazonaws.com/assets/example_white_firm_logo-e0c3f3d92f1388bb3781660e82e5efda.png"/>')
            }
        },
        show: "mousedown",
        hide: {
            event: "mousedown unfocus"
        },
        style: {
            classes: "qtip-light firm-logo-examples-tooltip"
        },
        position: {
            my: "bottom center",
            at: "top center",
            adjust: {
                y: -8
            }
        }
    })
}), $(function() {
    $("*[data-mask=phone]").mask("000-000-0000", {
        reverse: !0
    })
}), $(function() {
    $.pjax.defaults.timeout = 3e3
}), $(document).ready(function() {
    $(".advisor-dropdown").selectize({
        selectOnTab: !0
    })
});
var Spinner = {
    show: function(t) {
        var e = $(t);
        if (0 === e.find(".spinner-bg, .svg-circle-spinner").length) {
            var n = e.css("position");
            "relative" !== n && "absolute" !== n && e.css("position", "relative");
            var r = $(".loading").html();
            e.append(r)
        }
    },
    hide: function(t) {
        var e = $(t).find(".spinner");
        e.remove()
    }
};
! function(t, e) {
    var n = 2e3,
        r = 5e3,
        i = !1,
        o = null,
        a = null,
        s = function() {
            return e(".user-menu").is(":visible")
        },
        u = function() {
            s() ? c() : l()
        },
        l = function() {
            i || (e(".user-menu").show(), e(".user-welcome").addClass("open"), d())
        },
        c = function() {
            e(".user-menu").hide(), e(".user-welcome").removeClass("open"), a && clearTimeout(a)
        },
        f = function(t) {
            e(t.target).closest(".user-welcome").length || e(t.target).closest(".user-menu").length || c()
        },
        d = function() {
            s() && (a = setTimeout(c, r))
        },
        p = function() {
            a && clearTimeout(a)
        },
        h = function() {
            s() || (o = setTimeout(l, n))
        },
        g = function() {
            o && clearTimeout(o)
        };
    e(document).on("mousedown", ".user-welcome", u), e(document).on("mouseenter", ".user-menu", p), e(document).on("mouseleave", ".user-menu", d), e(document).on("mouseenter", ".user-welcome", h), e(document).on("mouseleave", ".user-welcome", g), e(document).on("click", f)
}(window, jQuery);