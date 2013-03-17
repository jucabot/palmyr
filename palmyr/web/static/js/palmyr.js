function capFirstLetter(string)
{
    return string.charAt(0).toUpperCase() + string.slice(1);
}

function roundNumber(num, dec) {
	var result = Math.round(num*Math.pow(10,dec))/Math.pow(10,dec);
	return result;
}

function stack_list(list) {
	var stacked_list = [];
	for (var i=0;i<list.length;i++)
	{
		var stack = list[i] + (i>0 ? stacked_list[i-1] : 0.0);
		stacked_list.push(stack);
	}
	return stacked_list;
}

function FeatureTableCommand(api_url,ftable_name)
{
	this.url = api_url;
	this.ftable_name = ftable_name;
	
	this.init = function() {

	}
	
	this._call_api = function (data, done) {
		$("body").css("cursor", "progress");
		return $.getJSON(
			this.url,
			data,
			function(data) {
				if (data.status == 'success' && done != null) {
					done(data);
				}
				if (typeof data.message != "undefined" && data.message != '') {
					$('#message').html('<div class="alert alert-' + data.status + '"><button type="button" class="close" data-dismiss="alert">&times;</button><strong>' + capFirstLetter(data.status) + '!</strong><br/>' + data.message + '</div>');
				}
				$("body").css("cursor", "auto");
			});

	}

	this.set_target = function (fname,done) {
		var cmd = 'set-target';
		this._call_api(
			{ 'ftable' : this.ftable_name, 'feature_name': fname, 'cmd' : cmd },
			function(response) {
					done();
			});
	}
	
	this.reset_target = function (done) {
		var cmd = 'reset-target';
		this._call_api(
			{ 'ftable' : this.ftable_name, 'cmd' : cmd },
			function(response) {
					done();
			});
	}

	this.set_class = function (fname,is_class,done) {
		var cmd = 'set-class';
		this._call_api(
			{ 'ftable' : this.ftable_name, 'feature_name': fname, 'cmd' : cmd, 'is_class': is_class },
			function(response) {
					done();
			});
	}

	this.use_feature = function (fname,use_it,done) {
		var cmd = 'use-feature';
		this._call_api(
			{ 'ftable' : this.ftable_name, 'feature_name': fname, 'cmd' : cmd, 'use_it': use_it },
			function(response) {
					done();
			});
	}
	
	this.toggle_feature = function (fname,done) {
		var cmd = 'toggle-feature';
		this._call_api(
			{ 'ftable' : this.ftable_name, 'feature_name': fname, 'cmd' : cmd },
			function(response) {
					done(response.fname,response.use);
			});
	}


	this.get_distribution_function = function(fname,draw_func) {
	
		var cmd = 'get-distribution-function';
		this._call_api(
			{ 'ftable' : this.ftable_name, 'feature_name': fname, 'cmd' : cmd },
			function(response) {
					draw_func(fname,response.data);
			});
	
	}
	
	this.build_model = function(done_func) {
	
		var cmd = 'build-model';
		this._call_api(
			{ 'ftable' : this.ftable_name, 'cmd' : cmd },
			function(response) {
					done_func(response.model_info);
			});
	}
	
	this.add_feature = function(name,type,code,done) {
	
		var cmd = 'add-feature';
		this._call_api(
			{ 'ftable' : this.ftable_name, 'cmd' : cmd, 'name':name, 'type':type,'code':code },
			function(response) {
					done();
			});
	}
	
	this.get_feature = function(name,done) {
	
		var cmd = 'get-feature';
		this._call_api(
			{ 'ftable' : this.ftable_name, 'cmd' : cmd, 'name':name },
			function(response) {
					done(response.feature);
			});
	}
	this.edit_feature = function(name,virtual_function_code,default_function_code,done) {
	
		var cmd = 'edit-feature';
		this._call_api(
			{ 'ftable' : this.ftable_name, 'cmd' : cmd, 'name':name,'virtual_function_code':virtual_function_code,'default_function_code':default_function_code },
			function(response) {
					done();
			});
	}
	this.remove_feature = function(name,done) {
	
		var cmd = 'remove-feature';
		this._call_api(
			{ 'ftable' : this.ftable_name, 'cmd' : cmd, 'name':name },
			function(response) {
					done();
			});
	}
	this.save_model = function(model_name,done) {
	
		var cmd = 'save-model';
		this._call_api(
			{ 'ftable' : this.ftable_name, 'cmd' : cmd },
			function(response) {
					done(response.name);
			});
	}
	
	this.save = function (filename) {
		var cmd = 'save';
		
		if (filename == '')  {
			this._call_api(
				{ 'ftable' : this.ftable_name, 'cmd' : cmd });
		}
		else {
			this._call_api(
				{ 'ftable' : this.ftable_name, 'filename': filename, 'cmd' : cmd });
		}
	}
	
	this.select_best_features = function (done) {
		var cmd = 'select-best-features';
		
		this._call_api(
			{ 'ftable' : this.ftable_name, 'cmd' : cmd },
			function(response) {
					done(response.kbest);
			});
		
	}
	
	this.get_model_info = function (name,done) {
		var cmd = 'get-model-info';
		
		this._call_api(
			{ 'ftable' : this.ftable_name, 'cmd' : cmd, 'name' : name },
			function(response) {
					done(response.model_info);
			});
		
	}
	
	this.get_current_model_info = function (done) {
		var cmd = 'get-current-model-info';
		
		this._call_api(
			{ 'ftable' : this.ftable_name, 'cmd' : cmd },
			function(response) {
					if (response.model_info != null)
						done(response.model_info);
			});
		
	}

	this.apply_prediction = function (model_name, input,output,done) {
		var cmd = 'apply-prediction';
		
		this._call_api(
			{ 'ftable' : this.ftable_name, 'cmd' : cmd, 'model-name': model_name, 'input' : input, 'output': output },
			function(response) {
					done();
			});
		
	}
	
	this.nl_query = function (query,done) {
		var cmd = 'nl-query';
		
		this._call_api(
			{ 'ftable' : this.ftable_name, 'cmd' : cmd, 'query': query },
			function(response) {
					done(response.type,response.data,response.query);
			});
		
	}
	
	

	this.init();

}


function draw_pie(name,x,render_to,title) {
	var chart;
		
	var options;
	options = {
		chart: {
			renderTo: render_to,
		},
		credits: {
			enabled: false
		},
		title: {
			text: title,
			x: -20 //center
		},
		
	    plotOptions: {
	                pie: {
	                    
	                    dataLabels: {
	                        enabled: true,
	                        color: '#000000',
	                        connectorColor: '#000000',
	                        formatter: function() {
	                            return '<b>' + name + ' ' + this.key +'</b> : (' + roundNumber(this.percentage,1) + '%)' ;
	                        }
	                    }
	                }
	    },
		series: [
			{
				type: 'pie',
				name: title,
			  	data : x.sort(function(a,b) {return a[1]-b[1]}).reverse().map(function (xy) { return [String(xy[0]),xy[1]];}),
			  	
			 }
		]
		
	};

	chart = new Highcharts.Chart(options);

}

function draw_bar(name,data,render_to,title,yTitle,min,show_label) {
	var chart;
	
	var options;
	
	show_label = typeof show_label !== 'undefined' ? show_label : false;
	min = typeof min !== 'undefined' ? min : 0;
	
	options = {
		chart: {
			renderTo: render_to,
			type: 'column',
			zoomType: 'x',
		},
		credits: {
			enabled: false
		},
		title: {
			text: title,
			x: -20 //center
		},
		xAxis: {
			categories: [],
			labels: {
          		enabled: true,
          		rotation: -45,
          		align: 'right',          
            },
		},
		yAxis: {
				min : min,
                title: {
                    text: yTitle,
                },
                minorTickInterval: 1.0,
        },
		tooltip: {
            formatter: function() {
                return '<b>'+ name + ' ' + this.x +'</b> : '+ this.y;
            }
        },
        plotOptions: {
            column: {
                pointPadding: 0.2,
                borderWidth: 0
            }
        },
        legend: {
                layout: 'vertical',
                backgroundColor: '#FFFFFF',
                align: 'left',
                verticalAlign: 'top',
                x: 100,
                y: 70,
                floating: true,
                shadow: true
            },
        series: [],
	
	};
	
	options.xAxis.categories = data.categories;
	options.series = data.series;
	
	chart = new Highcharts.Chart(options);

}

function draw_percent_stacked_bar(name,data,render_to,title,yTitle,min,show_label) {
	var chart;
	
	var options;
	
	show_label = typeof show_label !== 'undefined' ? show_label : false;
	min = typeof min !== 'undefined' ? min : 0;
	
	options = {
		chart: {
			renderTo: render_to,
			type: 'column',
			zoomType: 'x',
		},
		credits: {
			enabled: false
		},
		title: {
			text: title,
			x: -20 //center
		},
		xAxis: {
			categories: [],
			labels: {
          		enabled: true,
          		rotation: -45,
          		align: 'right',          
            },
            title: {
                    text: data.label_x,
                },
		},
		yAxis: {
				min : min,
                title: {
                    text: 'Distribution of ' + data.label_y,
                },
                minorTickInterval: 1.0,
        },
		tooltip: {
            formatter: function() {
                return '<b>'+ name + ' ' + this.series.name +'</b> : '+ Math.round(this.percentage,2)  +'%';
            }
        },
        plotOptions: {
            column: {
                pointPadding: 0.2,
                borderWidth: 0,
                stacking: 'percent'
                
            }
        },
        legend: {
                layout: 'horizontal',
                backgroundColor: '#FFFFFF',
                align: 'center',
               
                
                shadow: true
            },
        series: [],
	
	};
	
	options.xAxis.categories = data.categories;
	options.series = data.series;
	
	chart = new Highcharts.Chart(options);

}


function draw_wordcloud(name,data,render_to,title) {

	$('#' + render_to).html('');
	var fill = d3.scale.category20b();
	var w = 800;
	var h = 400;
	var max_words = 100;
	var scale_factor = 512; //100% --> font size
	
	
	function fade(opacity,text) {
	   
	     d3.selectAll(".word")
	         .filter(function(d) {
	           return d.text != text;
	         })
	       .transition()
	         .style("opacity", opacity);
	   
	}
	
	function text(d) {
		return d.text;
	}

	var words_data = [], word_dict= {} ;
	
	var max_size = 0;
	
	$.each(data.categories, function(i) {
		max_size =  Math.max(max_size,data.series[0].data[i]);
				
								
	});
	
	$.each(data.categories, function(i) {
		word = {text: data.categories[i], size: data.series[0].data[i]* scale_factor/max_size};
				
		words_data.push(word);
								
	});
	
	
	d3.layout.cloud().size([w, h])
	      .words(words_data)
	      .rotate(function() { return ~~(Math.random() * 2) * 90; })
	      .fontSize(function(d) { return d.size; })
	      .on("end", draw)
	      .start();
	
	 function draw(words) {
    	d3.select("#" + render_to).append("svg")
	        .attr("width",w )
	        .attr("height", h)
	      .append("g")
	        .attr("transform", "translate(" + [w >> 1, h >> 1] + ")")
	      .selectAll("text")
	        .data(words)
	      .enter().append("text")
	        .style("font-size", function(d) { return d.size + "px"; })
	        .style("cursor","pointer")
	        .style("fill", function(d) { return fill(d.text); })
	        .attr("class","word")
	        .attr("text-anchor", "middle")
	        .attr("transform", function(d) {
	          return "translate(" + [d.x, d.y] + ")rotate(" + d.rotate + ")";
	        })
	        .text(function(d) { return d.text; })
	        .on("mouseout", function(d) {
	        	fade(1,d.text);
	        	})
	        .on("mouseover", function(d) {
	        	fade(.1,d.text);
	        	
	        	})
	        ;
	  }
	  
	  
}

function draw_table(name,data,render_to,title) {

	var html = '';
	html += '<table class="table table-condensed">';
	html += '<thead><tr>';
	$.each(data.features,function (i) {
		html += '<th>' +  data.features[i] + '</th>';
	});
	html += '</tr></thead>';
	
	
	$.each(data.rows,function (i) {
		html += '<tr>';
		$.each(data.rows[i],function (j) {
			
			html += '<td>' + data.rows[i][j] + '</td>';
			
			});
			html += '</tr>';
		});
		
		
	html += '</table>';
	
	var query = '';
	html += '<div class="pagination">';
  	html += '<ul>';
  	if (data.has_prev) {
  		query = '(num_page:' + (data.page_num - 1) + ')';

  		html += '<li><a href="#top" onclick="ftcmd.nl_query(\'' + query + '\', display_result);">&laquo;</a></li>'
  	}
    $.each(data.list_pages,function (i) {
    	var num_page = 0;
    	num_page = data.list_pages[i]+1;
    	query = '(num_page:' + i + ')';
    	if (i == data.page_num) {
	    	html += '<li class="active"><a href="#top" onclick="ftcmd.nl_query(\'' + query + '\', display_result);">' + num_page + '</a></li>'
	    }
	    else {
	    	html += '<li><a href="#top" onclick="ftcmd.nl_query(\'' + query + '\', display_result);">' + num_page + '</a></li>'
	    }
    });
  	if (data.has_next) {
  		query = '(num_page:' + (data.page_num + 1) + ')';
  		html += '<li><a href="#top" onclick="ftcmd.nl_query(\'' + query + '\', display_result);">&raquo;</a></li>'
  	}

    html += '</ul>';
	html += '<div class="pull-right">';
	html += 'page ' + (data.page_num + 1) +'/' + data.page_total;
	html += '&nbsp; total rows ' + data.num_total_rows;
	html += '</div>';
	html += '</div>';
	$('#'+render_to).html(html);
	
}
/*
function draw_mosaic_box(name,data,render_to,title,xTitle,yTitle) {
	$('#' + render_to).html('');
	var margin = {top: 40, right: 20, bottom: 50, left: 60},
	    width = 860 - margin.left - margin.right,
	    height = 500;
	
	var margin_box = 2;
	
	var formatPercent = d3.format(".0%");
	
	var label_x = xTitle;
	var label_y = yTitle;
	var classes = data.classes;
	var series = data.series;
	
	
	var pos_x = 0.0;
	var pos_y = 0.0;
	var boxes = [];
	var last_x = 0.0;
	var range_x = [];
	var range_y = [];
	
	for (var i=0;i<classes[0].length;i++)
	  {
		pos_y = 0.0;
		
	 	for (var j=0;j<classes[1].length;j++)
	  	{
			var box = series[i*classes[1].length+j];
			box.x = pos_x;
			last_x = box.w;
			box.y = pos_y;
			pos_y += box.h;
			box.class_x = classes[0][i];
			box.class_y = classes[1][j];
			
		}
		pos_x += last_x;
		
		range_x.push(last_x);
		
	  }
	
	for (var j=0;j<classes[1].length;j++)
	{
		range_y.push(series[j].h);	
	}
	var stack_x = stack_list(range_x);
	
	var stack_y = stack_list(range_y);
	         
	
	var svg = d3.select("#" + render_to).append("svg")
		.attr("width", width + margin.left + margin.right)
		.attr("height", height + margin.top + margin.bottom)
		.attr("class", "box-bg")
		.append("g")
			.attr("transform", "translate(" + margin.left + "," + margin.top + ")")
	
	
	svg.selectAll(".box-bg")
		.data(classes[0])
		.enter().append("text")
			.attr("font-size","90%")
			.attr("font-weight","bold")
			.text(function (d) {return d; })
			.attr("x", function(d)  { var i = classes[0].indexOf(d); return (stack_x[i] - series[i*classes[1].length].w/2 ) * width -this.getComputedTextLength()/2; })
			.attr("y", function(d)  { return height +10; })
			
	svg.selectAll(".box-bg")
		.data(classes[1])
		.enter().append("text")
			.text(function (d) {return d; })
			.attr("font-size","90%")
			.attr("font-weight","bold")
			.attr("y", -5)
			.attr("x", function(d)  { var i = classes[1].indexOf(d); return -(stack_y[i] - series[i].h/2) * height - this.getComputedTextLength()/2; })
			.attr("transform", "rotate(-90) ")
	  
	  
	svg.append("g")
		.append("text")
			.text(label_y)
			.attr("transform", "rotate(-90) ")
			.attr("x",function (d) {return -height/2+ this.getComputedTextLength()/2;})
			.attr("y",-40)
			.attr("style","font-size : 130%;font-weight: bold;")  
	
	svg.append("g")
		.append("text")
			.text(label_x)
			.attr("x",function (d) {return width/2 - this.getComputedTextLength()/2; })
			.attr("y",height + 50)
			.attr("style","font-size : 130%;font-weight: bold;") 
	
	 
	svg.selectAll(".box")
		.data(series)
		.enter().append("rect")
			.attr("fill", "steelblue")
			.attr("style", "border: solid 5px white;")
			.attr("x", function(d)  { return d.x * width + 1; })
			.attr("width", function(d) { return d.w * width - 2 ; })
			.attr("y", function(d) { return d.y * height + 1 ; })
			.attr("height", function(d) { return d.h * height - 2 ; })
	
	svg.selectAll(".box-bg")
		.data(series)
		.enter().append("text")
			.text(function (d) {return d.class_x + " : " + Math.round(d.w * 100) + '%'; })
			.attr("x", function(d)  { return (d.x+ d.w/2) * width - this.getComputedTextLength()/2 ; })
			.attr("y", function(d)  { return (d.y+ d.h/2) * height - 10; })
			.attr("fill", "white")
			.attr("style","font-size:90%;")
	
	svg.selectAll(".box-bg")
		.data(series)
		.enter().append("text")
			.text(function (d) {return d.class_y + " : " +  Math.round(d.h * 100) + '%'; })
			.attr("x", function(d)  { return (d.x+ d.w/2) * width - this.getComputedTextLength()/2 ; })
			.attr("y", function(d)  { return (d.y+ d.h/2) * height  + 10; })
			.attr("fill", "white")
			.attr("style","font-size:90%;")
			

}
*/
function draw_scatter(name,data,render_to,title,xTitle,yTitle,show_label) {
	var chart;
	
	var options;
	
	show_label = typeof show_label !== 'undefined' ? show_label : false;
	
	
	options = {
		chart: {
			renderTo: render_to,
			type: 'scatter',
            zoomType: 'xy'
		},
		credits: {
			enabled: false
		},
		title: {
			text: title,
			x: -20 //center
		},
		xAxis: {
			title: {
                    enabled: true,
                    text: data.label_x
                },
	        startOnTick: true,
	        endOnTick: true,
	        showLastLabel: true
		},
		yAxis: {
				
                title: {
                    text: data.label_y,
                },
                minorTickInterval: 1.0,
                startOnTick: true,
	        endOnTick: true,
	        showLastLabel: true
        },
		tooltip: {
            formatter: function() {
                return  data.label_x + ' = ' + this.x +' : ' + data.label_y + ' = ' + this.y;
            }
        },
        plotOptions: {
            scatter: {
                    marker: {
                        radius: 5,
                        states: {
                            hover: {
                                enabled: true,
                                lineColor: 'rgb(100,100,100)'
                            }
                        },
                        
                    },
                    states: {
                        hover: {
                            marker: {
                                enabled: false
                            }
                        }
                    }
                }
        },
       
        series: [],
	
	};
	data.series[0]['color'] = 'rgba(68,136,187,0.5)';
	options.series = data.series; 
	
	
	
	chart = new Highcharts.Chart(options);

}

function draw_box_plot(name,data,render_to,title)
{
	var options = {
			chart: {
		        type: 'boxplot',
		        renderTo: render_to,
		        zoomType:'xy',
		    },
		    
		    title: {
		        text: 'Distribution of ' + data.label_y + ' by ' + data.label_x
		    },
		    credits: {
		        enabled: false
		    },
		    
		    legend: {
		        enabled: false
		    },
		
		    xAxis: {
		        categories: data.categories,
		        title: {
		            text: data.label_x
		        }
		    },
		    
		    yAxis: {
		        title: {
		            text: data.label_y
		        },
		        minorTickInterval: 1.0,
		        
		    },
		
		    series: [{
		        name: data.label_y,
		        data: data.series,
		        tooltip: {
		            headerFormat: '<em>' + data.label_y + ' {point.key}</em><br/>'
		        }
		    },
		    
		    /* {
		        name: 'Outlier',
		        color: Highcharts.getOptions().colors[0],
		        type: 'scatter',
		        data: [ // x, y positions where 0 is the first category
		            [0, 644],
		            [4, 718],
		            [4, 951],
		            [4, 969]
		        ],
		        marker: {
		            fillColor: 'white',
		            lineWidth: 1,
		            lineColor: Highcharts.getOptions().colors[0]
		        },
		        tooltip: {
		            pointFormat: 'Observation: {point.y}'
		        }
		    }
		    */
		    ]
	
		};

	var chart = new Highcharts.Chart(options);
}

