!function (){
   window.onload = function () {
       url = document.getElementsByName("articel_url")[0]
       button = document.getElementsByTagName("button")[0]
       button.onclick = function () {
           $.ajax(

               {
                   "type": "POST",
                   "url": "/check/articel/",
                   "data": {"link":url.value},
                   "dataType": "json",
                   "success": function (data, status, httpxhr) {

                       if(data['code'] == 4){
                            // var title = data['title'];
                            // var passages_count = data['passages_count'];
                            // var keyword = data['keyword'];
                            // var origin = data['origin'];
                            // var count = data['count'];
                            // var time = data['time'];
                            // var type = data['type'];
                            //
                           var str = "";
                           var temp = "";
                           for(var i in data){
                               if(i == "title"){
                                   temp = "文章标题："
                               }
                               else if(i == "passages_count"){
                                   temp = "段落数目："
                               }
                               else if(i == "keyword"){
                                   temp = "关键词："
                               }
                               else if(i == "origin"){
                                   temp = "文章来源："
                               }
                               else if(i == "count"){
                                   temp = "文章字数："
                               }
                               else if(i == "time"){
                                   temp = "发布时间："
                               }
                               else if(i == "type"){
                                   temp = "文章类型："
                               }
                               else{
                                   continue
                               }
                               str += "<p><span>" + temp + "</span><span>" + data[i] + "</span></p>";

                           }
                           $(".check").css('background-color', '#eee').html(str);


                       }
                       else{
                           $(".check").html('查询出错，请重新查询！')
                       }
                       // console.log(data)
                       // console.log(status)
                       // console.log(httpxhr)

                   }
               }
           )
       }
   }
   $(document).ajaxStart(function () {
       $(".check").html('正在分析文章...')
   })
}()
