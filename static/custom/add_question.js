$(document).ready(function () {
    let dists_all = $("#qq");
    let added_dists = $("#dists");
    let number_counter = 0;

    $("#bb").click(function () {
        let val_dist = dists_all.val();
        if (val_dist === "") {
            $("#qq").css({'border': '2px solid red !important'});
            return false;
        } else {
            number_counter += 1;
            added_dists.html(`${added_dists.html()}
                                <tr>
                                    <td class="text-danger"><input id="del_item_${number_counter}" type="button" class="text-danger" 
                                    hidden/>
                                    <label for="del_item" class="del_choice"><i style="cursor: pointer" class="fas fa-trash"></i></label>
                                    </td>
                                    <td class="choice">${val_dist}</td>
                                    <td><input type="checkbox" class="form-control is_correct"/></td>
                                </tr>`
            );
            dists_all.val("");
            return false;
        }
    });

    $('#goo').click(function () {
        let my_list = [];
        let correct_in_list = [];
        let values_in_list = [];
        $('tbody > tr').each(function (index, tr) {
            let choice_val = '';
            let choice_is_correct = false;
            $(this).find('.choice').each(function (index, td) {
                choice_val = $(td).html();
            });
            $(this).find('.is_correct').each(function (index, input) {
                if ($(input).is(':checked')) {
                    choice_is_correct = true;
                }
            });

            my_list.push(`{"value": "${choice_val}", "is_correct": ${choice_is_correct}}`);
            correct_in_list.push(choice_is_correct);
            values_in_list.push(choice_val);
        });

        if (my_list.length < 2) {
            $('#num_choices').css({'border': "2px solid red"});
            return false;
        } else if ($.inArray(true, correct_in_list) < 0) {
            $('#num_correct').css({'border': "2px solid red"});
            return false;
        } else {
            for (let i = 0; i < values_in_list.length - 1; i++) {
                if ($.inArray(values_in_list[i + 1], values_in_list) > 0) {
                    console.log("error");
                    break;
                }
            }
            $('#choices_dists').val(JSON.stringify(my_list));
            return $(this).submit();
        }
    });

    $(document).on('click', '.del_choice', function () {
        $(this).parent().parent().remove();
    });
});
