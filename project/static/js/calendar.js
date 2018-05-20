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
        events: function (start, end, timezone, callback) {
            $.ajax({
                url: '/api/dinners?start=' + start.toISOString(),
                color: 'red',
                textColor: 'black',
                success: function (data) {
                    var events = [];
                    data["dinners"].forEach(function (dinner) {
                        events.push(dinner);
                    });
                    callback(events);
                },
                error: function (error) {
                    alert("Couldn't get data from URL " + error);
                },
            })

        },
        eventClick: function (event) {
            if (event.url) {
                window.open('/dinner_club/meal/' + event.url, '_self');
                return false;
            }
        }

    });
}