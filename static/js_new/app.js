var fontFamily = 'Roboto';
var fontSize = 14;

var App = {

  _isWithTooltips: false,

  config: {
    chart: {
      defaults: {
        title: {
          fontFamily: fontFamily,
        },
        tooltips: {
          fontFamily: fontFamily,
        },
        legend: {
          fontFamily: fontFamily,
        },
      },
    },
    lineChart: {
      options: {
        common: {
        },
        worth: {
          tooltips: {
            callbacks: {
              title: function(values) {
                return Number(values[0].xLabel.toFixed(0)) + ' years';
              },
              label: function(values) {
                return '$' + Number(values.yLabel.toFixed(0)).toLocaleString();
              },
            },
          },
          scales: {
            xAxes: [
              {
                type: 'linear',
                id: 'x-axis-1',
                position: 'bottom',
                scaleLabel: {
                  display: true,
                  labelString: 'Age',
                  fontFamily: fontFamily,
                  fontSize: fontSize,
                },
                ticks: {
                  min: 20,
                  max: 70,
                  fontFamily: fontFamily,
                  fontSize: fontSize,
                },
              }
            ],
            yAxes: [
              {
                type: 'linear',
                id: 'y-axis-1',
                position: 'left',
                scaleLabel: {
                  display: true,
                  //labelString: 'Net worth',
                  fontFamily: fontFamily,
                  fontSize: fontSize,
                },
                ticks: {
                  min: 0,
                  suggestedMax: 100000,
                  fontFamily: fontFamily,
                  fontSize: fontSize,
                  callback: function(value) {
                    return '$' + Number(value.toFixed(0)).toLocaleString();
                  },
                },
              },
              {
                type: 'linear',
                id: 'y-axis-2',
                position: 'right',
                scaleLabel: {
                  display: true,
                  //labelString: 'Cashflow',
                  fontFamily: fontFamily,
                  fontSize: fontSize,
                },
                ticks: {
                  min: 0,
                  suggestedMax: 100000,
                  fontFamily: fontFamily,
                  fontSize: fontSize,
                  callback: function(value) {
                    return '$' + Number(value.toFixed(0)).toLocaleString();
                  },
                },
              },
            ],
          },
        },
        events: {
          tooltips: {
            callbacks: {
              title: function(values) {
                if (Number(values[0].xLabel.toFixed(0)) >= 70) {
                  return '70+ years';
                } else {
                  return Number(values[0].xLabel.toFixed(0)) + ' years';
                }
              },
              label: function(values) {
                return '$' + Number(values.yLabel.toFixed(0)).toLocaleString();
              },
            },
          },
          scales: {
            xAxes: [{
              type: 'linear',
              id: 'x-axis-1',
              position: 'bottom',
              scaleLabel: {
                display: true,
                labelString: 'Average Age at Completion',
                fontFamily: fontFamily,
                fontSize: fontSize,
              },
              ticks: {
                min: 20,
                max: 70,
                fontFamily: fontFamily,
                fontSize: fontSize,
              },
            }],
            yAxes: [{
              id: 'y-axis-1',
              position: 'left',
              scaleLabel: {
                display: true,
                labelString: 'Average Target Amount',
                fontFamily: fontFamily,
                fontSize: fontSize,
              },
              ticks: {
                min: 0,
                suggestedMax: 100000,
                fontFamily: fontFamily,
                fontSize: fontSize,
                callback: function(value) {
                  return '$' + Number(value.toFixed(0)).toLocaleString();
                },
              },
            }],
          },
        },
      }
    },

    doughnutChart: {
      options: {
        common: {
          legend: {
            display: false,
          },
          tooltips: {
            callbacks: {
              label: function(indexes, context) {
                var value = parseFloat(context.datasets[indexes.datasetIndex].data[indexes.index]);
                var label = context.labels[indexes.index];
                return '' + label + ': ' + '$' + Number(value.toFixed(0)).toLocaleString();
              },
            },
          },
        },
        risk: {
          legend: {
            display: true,
            position: 'bottom',
          },
        }
      },
      /* OBSOLETED
      backgroundColor: [
        '#F7464A',
        '#46BFBD',
        '#FDB45C',
      ],
      hoverBackgroundColor: [
        '#FF5A5E',
        '#5AD3D1',
        '#FFC870',
      ],
      */
    },
  },

  init: function() {
    App._tooltips();
    App._remote(); // auto load remote content

    $(window).on('resize', App._tooltips);

    $(document).on('shown.bs.tab', function() {
      $(document).trigger('redraw.bs.charts');
    });

    $(document).on('hidden.bs.modal', function(e) {
      $(e.target).removeData('bs.modal').find('.modal-content.modal-content-remote').empty();
    });

    Chart.defaults.global.title.fontFamily = this.config.chart.defaults.title.fontFamily;
    Chart.defaults.global.tooltips.titleFontFamily = this.config.chart.defaults.tooltips.fontFamily;
    Chart.defaults.global.tooltips.bodyFontFamily = this.config.chart.defaults.tooltips.fontFamily;
    Chart.defaults.global.tooltips.footerFontFamily = this.config.chart.defaults.tooltips.fontFamily;
    Chart.defaults.global.legend.labels.fontFamily = this.config.chart.defaults.legend.fontFamily;
    Chart.defaults.global.legend.labels.fontSize = 14;
  },

  _tooltips: function() {
    if ($(window).width() > 768) {
      if (App._isWithTooltips) { return; }

      App._isWithTooltips = true;
      $('[data-toggle="tooltip"]').tooltip();

    } else {
      if (!App._isWithTooltips) { return; }

      App._isWithTooltips = false;
      $('[data-toggle="tooltip"]').tooltip('destroy');
    }
  },

  _remote: function() {
    // Experimental (not in use)
    $('[data-remote="true"]').each(function(index, elem) {
      elem = $(elem);
      var href = elem.attr('href');
      var target = $(elem.attr('data-target') || elem);

      if (!href) { return; }

      elem.on('click', function(e) {
        e.preventDefault();

        $.get(href, function(data) {
          target.html(data);
        });

      });
    });
  },

  doughnutChartConfig: function(labels, values, backgroundColors, hoverBackgroundColors) {
    /*
      @lavels: array
      @values: array of numbers
     */
    return {
      type: 'doughnut',
      data: {
        labels: labels,
        datasets: [
          {
            data: values,
            backgroundColor: backgroundColors || [],
            hoverBackgroundColor: hoverBackgroundColors || backgroundColors || [],
          }
        ],
      },
      options: this.config.doughnutChart.options.common,
    }
  },

  lineChartConfig: function() {
    // RESERVED
    return {}
  },

  worthLineChartConfig: function(datasets) {
    /*
      @datasets: array
    */

    // TODO: temp temp temp
    datasets_config = [{
      yAxisID: 'y-axis-1',
      fill: true,
      backgroundColor: 'rgba(200,150,200,0.2)',
      borderColor: 'rgba(200,150,200,1)',
      pointBorderColor: 'rgba(200,150,200,1)',
      pointBackgroundColor: '#fff',
      pointBorderWidth: 1,
      pointHoverRadius: 5,
      pointHoverBackgroundColor: 'rgba(200,150,200,1)',
      pointHoverBorderColor: 'rgba(200,150,200,1)',
      pointHoverBorderWidth: 2,
    },
    {
      yAxisID: 'y-axis-2',
      fill: false,
      backgroundColor: 'rgba(120,220,180,0.2)',
      borderColor: 'rgba(120,220,180,0.7)',
      pointBorderColor: 'rgba(120,220,180,1)',
      pointBackgroundColor: '#fff',
      pointBorderWidth: 1,
      pointHoverRadius: 5,
      pointHoverBackgroundColor: 'rgba(120,220,180,1)',
      pointHoverBorderColor: 'rgba(120,220,180,1)',
      pointHoverBorderWidth: 2,
    }];

    datasets = datasets || [];
    datasets = datasets.map(function(item, index) {
      return $.extend({}, item, datasets_config[index]);
    });

    return {
      type: 'line',
      data: {
        datasets: datasets,
      },
      options: $.extend(
        this.config.lineChart.options.common,
        this.config.lineChart.options.worth
      ),
    }
  },

  eventsLineChartConfig: function(datasets) {
    /*
      @datasets: array
    */

    datasets = datasets || [];
    var x = 1
    datasets = datasets.map(function(item) {
      x++;
      background = randomColor({
        seed: x * 849,
        luminosity: 'bright',
        format: 'rgb'
      });
      return $.extend({}, item, {
        borderColor: background,
        //pointBorderColor: "rgba(200,150,200,1)",
        pointBackgroundColor: background,
        //pointHoverBackgroundColor: "rgba(200,150,200,1)",
        //pointHoverBorderColor: "rgba(200,150,200,1)",
        pointBorderWidth: 9,
        pointHoverRadius: 10,
      })
    });

    return {
      type: 'line',
      data: {
        datasets: datasets,
      },
      options: $.extend(
        this.config.lineChart.options.common,
        this.config.lineChart.options.events
      ),
    }
  },

}

App.init()