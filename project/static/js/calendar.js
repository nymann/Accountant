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
        eventSources: [{
            url: '/api/dinners',
            color: 'red',
            textColor: 'black',
            error: function (error) {
                alert("Couldn't get data from URL " + error);
            },
        }],
        eventClick: function (event) {
            if (event.url) {
                window.open('/dinner_club/meal/' + event.url, '_self');
                return false;
            }
        }
    });
}