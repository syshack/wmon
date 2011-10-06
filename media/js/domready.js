Date.prototype.monthNames = [
	"January", "February", "March",
	"April", "May", "June",
	"July", "August", "September",
	"October", "November", "December"
];

Date.prototype.getMonthName = function() {
	return this.monthNames[this.getMonth()];
};
Date.prototype.getShortMonthName = function () {
	return this.getMonthName().substr(0, 3);
};

Dygraph.prototype.parseFloat_ = function(x, opt_line_no, opt_line) {
  var val = parseFloat(x);
  if (!isNaN(val)) return val;
  return x;
};

window.addEvent('domready',function(){

	var hosts = JSON.decode(Cookie.read('showhosts')) || [];
	hosts.each(function(el){
		$(el).addClass('none');
	});
	
	$$('div.hostname').addEvent('click',function(){
		var host = this.getNext('div');
		host.toggleClass('none');
		
		if(hosts.indexOf(host.get('id'))!=-1) hosts.erase(host.get('id'));
		else hosts.push(host.get('id'));
		
		Cookie.write('showhosts', JSON.encode(hosts));
	})

});
