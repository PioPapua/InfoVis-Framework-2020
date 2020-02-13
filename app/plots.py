from bokeh.plotting import figure, ColumnDataSource
from bokeh.layouts import row, column, widgetbox
from bokeh.models import HoverTool, Slider, CustomJS
from bokeh.embed import json_item

from . import data

def create_hbar(area, plot_data, y_variables=data.model_vars, y_definition=data.label_def_ordered, 
y_extra_info=data.label_extra_ordered, div_name="myplot"):
	values = plot_data.to_numpy()
	values = values[0]

	all_data = ColumnDataSource(data=dict({'variables': y_variables,
				'values': values,
				'definition': y_definition,
				'variables_extra': y_extra_info}))

	tooltips = """
	<div style="width:200px;">
			<div>
				<span style="font-size: 15px; color:blue">Variable:</span>
				<span style="font-size: 12px;">@variables_extra</span>
			</div>
			<div>
				<span style="font-size: 15px; color:blue">Percentage:</span>
				<span style="font-size: 12px;">@values{1.1} %</span>
			</div>
			<div>
				<span style="font-size: 15px; color:blue">Explanation:</span>
				<span style="font-size: 12px;">@definition</span>
			</div>
		</div>
	"""

	shade0 = '#592A71'
	shade1 = '#9874AA'
	shade2 = '#774A8E'
	shade3 = '#3E1255'
	shade4 = '#260339'

	cshade0 = '#A8AA39'
	cshade1 = '#FDFEAA'
	cshade2 = '#D3D46A'
	cshade3 = '#7E7F15'
	cshade4 = '#545500'

	hover = HoverTool( mode='vline', line_policy='nearest', names=['bar']
	)

	plot = figure(plot_height = 600, plot_width = 800, 
			  x_axis_label = 'Percentage', 
			   #y_axis_label = ,
			   x_range=y_variables, y_range=(0,100), tools= [hover,"save","pan","box_zoom","reset","wheel_zoom"], tooltips=tooltips)



	plot.ygrid.band_fill_alpha = 0.05
	plot.ygrid.band_fill_color = shade0
	plot.xaxis.major_label_orientation = -3.14 * 0.25


	#DataFrame.plot.scatter(self, x, y, s=None, c=None, **kwargs)
	#plot.hbar(left='values', y='variables', right=1, height=0.9, fill_color='red', line_color='black', fill_alpha = 0.75,
	#        hover_fill_alpha = 1.0, hover_fill_color = 'navy', source=all_data)


	plot.triangle(x='variables', y='values', line_width=1, source=all_data, size=55, color = cshade1,  fill_alpha = 0.15)
	
	plot.text(x='variables', y='values', text='values', text_font_size='18pt',
       text_baseline="bottom", text_align="center", source=all_data)

	plot.vbar(x='variables', bottom=0, top='values', name='bar' ,
		width=0.75,   line_dash = [6, 3],
		hover_fill_alpha = 1.0, hover_fill_color = cshade1,
		color = shade1, line_color=cshade0, fill_alpha = 0.65,
		legend='Rental Type', source=all_data)

	plot.title.text = "Relevant statistics about " + area
	#plot.hbar(left='values', y='variables', right=1, height=0.9, fill_color='red', line_color='black', fill_alpha = 0.75,
	#        hover_fill_alpha = 1.0, hover_fill_color = 'navy', source=all_data)
	
	part_rent_slider = Slider(start=0, end=100, value=plot_data.loc[:, 'WPARTHUUR_P'].iloc[0], step=1, title="Private rental")
	corp_rent_slider = Slider(start=0, end=100, value=plot_data.loc[:, 'WCORHUUR_P'].iloc[0], step=1, title="Housing corporation rental")
	high_rent_slider = Slider(start=0, end=100, value=plot_data.loc[:, 'WHUURHOOG_P'].iloc[0], step=1, title="High rent (> 971 euro)")
	middle_rent_slider = Slider(start=0, end=100, value=plot_data.loc[:, 'WHUURMIDDEN_P'].iloc[0], step=1, title="Middle high rent (711 - 971 euro)")
	low_rent_slider = Slider(start=0, end=100, value=plot_data.loc[:, 'WHUURTSLG_P'].iloc[0], step=1, title="Low rent (< 711 euro)")
	living_space_040 = Slider(start=0, end=100, value=plot_data.loc[:, 'WOPP0040_P'].iloc[0], step=1, title="Living space of 0-40 m2")
	living_space_4060 = Slider(start=0, end=100, value=plot_data.loc[:, 'WOPP4060_P'].iloc[0], step=1, title="Living space of 40-60 m2")
	living_space_6080 = Slider(start=0, end=100, value=plot_data.loc[:, 'WOPP6080_P'].iloc[0], step=1, title="Living space of 60-80 m2")
	living_space_80100 = Slider(start=0, end=100, value=plot_data.loc[:, 'WOPP80100_P'].iloc[0], step=1, title="Living space of 80-100 m2")
	living_space_100 = Slider(start=0, end=100, value=plot_data.loc[:, 'WOPP100PLUS_P'].iloc[0], step=1, title="Living space of > 100 m2")

	all_sliders = [part_rent_slider, corp_rent_slider, high_rent_slider,middle_rent_slider, low_rent_slider, 
	living_space_100, living_space_80100, living_space_6080, living_space_4060, living_space_040]

	callback = CustomJS(args=dict(source=all_data), code="""
		var data = source.data;
		var values = data["values"];

		var value = cb_obj.value;
		var var_text = cb_obj.title;

		var variable;
		var value_idx;
		updatePlot(value, var_text);
		socket.on('plot_update', function(msg) {
			value = msg.new_value;
			variable = msg.variable;
			value_idx = msg.index;

			values[value_idx] = value;
			data.values = values;
			source.data = data;
			source.change.emit();

			window.onmouseup = function() {
				updateModel(value, variable);
			}
		});
	""")

	for slider in all_sliders:
		slider.js_on_change('value', callback)

	layout = row(
		plot,
		column(*all_sliders),
		width=800
	)

	plot_json = json_item(layout, div_name)

	return plot_json