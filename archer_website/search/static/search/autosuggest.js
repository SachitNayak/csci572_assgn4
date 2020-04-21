function searchOpen() {
            var search_value = $('#search_box').val()
            var data = {
                q: search_value,
                wt :'json'
            };
            $.ajax({
                url: 'http://localhost:8983/solr/latimes_core/suggest',
                data: data,
                dataType: 'jsonp',
                cors: true ,
              secure: true,
              headers: {
                'Access-Control-Allow-Origin': '*',
              },
                jsonp: 'json.wrf',
                jsonpCallback: 'searchResult'
            });
        }


        function searchResult(data) {
            var q = $('#search_box').val();
            var val = data.suggest.suggest;
            var res = val[q].suggestions;
            var data_arr = [];
            for(var i in res){
                data_arr.push(res[i]["term"]);
            }
            console.log(q);
            console.log(data_arr);
            $( "#search_box" ).autocomplete({
                source: function (request, response) {
                    response(data_arr);
                }
            });
        }