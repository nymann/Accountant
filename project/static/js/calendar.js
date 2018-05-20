function calendarInit(defaultView, defaultDate) {
    $('#calendar').fullCalendar({
        header: {
            left: 'prev,next today',
            center: 'title',
            defaultView: defaultView,
            right: 'month, basicWeek,basicDay'
        },
        defaultDate: defaultDate,
        allDay: true,
        navLinks: true,
        editable: false,
        eventLimit: true,
        events: {
            url: '/api/dinners',
            error: function (error) {
                alert("Couldn't get data from URL " + error);
            }
        },
        eventClick: function (event) {
            if (event.url) {
                window.open('/dinner_club/meal/' + event.url);
                return false;
            }
        },
        eventRender: function (event, element) {
            element.css({
               'background-color': '#ff1e00',
                'border-color': '#ff1e00',
                'color': '#ff1e00'
            });
        }
    });
}