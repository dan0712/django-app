/**
 * Created by cristian on 2/01/16.
 */

/*
    https://github.com/Microsoft/TypeScript-Handbook/blob/master/pages/Mixins.md
    mixed classes
 */
"use strict";

function applyMixins(derivedCtor, baseCtors) {
    baseCtors.forEach(function (baseCtor) {
        Object.getOwnPropertyNames(baseCtor.prototype).forEach(function (name) {
            derivedCtor.prototype[name] = baseCtor.prototype[name];
        });
    });
}
