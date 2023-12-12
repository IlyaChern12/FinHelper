$(function() {
	// проверка для нажатия на кнопку выбрать все
	$("#check_all").on("click", function () {
		if ($("input:checkbox").prop("checked")) {
			$("input:checkbox[name='row-check']").prop("checked", true);	// установление чекбокса в True
		} else {
			$("input:checkbox[name='row-check']").prop("checked", false);	// отключение чекбоксов при повторном нажатии
		}
	});

	// обработка выбора чекбокса в каждой строке
	$("input:checkbox[name='row-check']").on("change", function () {		// вызов только при изменении значения чекбокса
		var total_check_boxes = $("input:checkbox[name='row-check']").length;	// количество всех чекбоксов
		var total_checked_boxes = $("input:checkbox[name='row-check']:checked").length;	// количество выбранных

		// если выбраны все чеки то автоматически выбирается и верхний в шапке таблицы
		if (total_check_boxes === total_checked_boxes) {
			$("#check_all").prop("checked", true);
		}
		else {
			$("#check_all").prop("checked", false);
		}
	});
	
	// удаление элементов с указанием на кнопку запуска #delete_notes
	$("#delete_notes").on("click", function () {
		var ids = '';
		var comma = '';

		// запись чекбоксов для удаления и формирование списка ids, состоящего из данных по записям
		$("input:checkbox[name='row-check']:checked").each(function() {
			ids = ids + comma + this.value; // добавление текущих данных для уже записанных
			comma = ',';			
		});		
		
		// обработка сообщений
		if(ids.length > 0) {
			$.ajax({
				type: "POST",
				contentType: 'application/json;charset=UTF-8',
				url: "/delete_notes",
				data: JSON.stringify({'ids': ids}),
				dataType: "json",
				cache: false,
				// успешное удаление
				success: function(msg) {
					$("#msg").html(msg);	// вывод сообщения в объект с id #msg
					setTimeout(function() {
						location.reload();	// перезагрузка страницы после задержки в 900 милисекунд 
					}, (900));
					
					
				},
				// непредвиденная ошибка удаления
				error: function(jqXHR, textStatus, errorThrown) {					
					$("#msg").html("<span style='color:red;'>" + textStatus + " " + errorThrown + "</span>");
				}
			});
		// не выбраны элементы
		} else {
			$("#msg").html("<div class='bad_add'>Для удаления выберите хотя бы один элемент</div>");
		}
	});
});