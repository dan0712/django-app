var gulp = require('gulp');
var ts = require('gulp-typescript');
var merge = require('merge2');
var babel = require('gulp-babel');
var include  = require("gulp-include");
var insert = require('gulp-insert');
var uglify = require('gulp-uglify');
var sourcemaps = require('gulp-sourcemaps');


/*
 *  ======================================================================
 *   bundle  third party libraries https://github.com/wiledal/gulp-include
 *  ======================================================================
*/

var vendors_bundle="//=require libs/underscore.js\n\
//=require libs/angular-1.4.js\n\
//=require libs/angular-ui-router.js\n\
//=require libs/restangular.js\n"


var tsProject = ts.createProject('tsconfig.json');

/*
 * Compile betasmartz client app
 */
gulp.task('compile_dev', function() {
    var tsResult = gulp.src('src/application.ts').pipe(sourcemaps.init()).pipe(ts(tsProject));

    return merge([ // Merge the two output streams, so this task is finished when the IO of both operations are done.
        tsResult.dts.pipe(gulp.dest('public/definitions')),
        tsResult.js.pipe(babel({ presets: ['es2015']}))
            .pipe(insert.prepend(vendors_bundle))
            .pipe(include())
            .pipe(sourcemaps.write('../js'))
            .pipe(gulp.dest('public/js'))
    ]);
});



/*
 * Publish html files
 */
gulp.task('publish_views', function() {
    gulp.src(["src/views/**/*"]).pipe(gulp.dest('public/views'));

});


/*
 * Build app
 */
gulp.task('build_dev', ['publish_views', 'compile_dev']);



gulp.task('watch', ['build_dev'], function() {
    gulp.watch('src/**/*', ['build_dev']);
});