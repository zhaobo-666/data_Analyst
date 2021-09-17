$(function () {
       //去除特殊字符函数
        String.prototype.rep_str=function(){
          //[]内输入你要过滤的字符，这里是我的
          let pattern=new RegExp("[`~%!@#^\"=''?~《》！@#￥……&——‘”“'？*()（），,。.、<>]");
          let rs="";
          for(let i=0;i<this.length;i++){
              rs+=this.substr(i,1).replace(pattern,'');
          }
          return rs;
        }

       //退出
       $('#login_out').click(function () {
           location.href="/signout";
       });

        //新增数据库
        $('.sub_sqlmessage').click(function () {
             var host = $('#host').val();
             var db = $('#db').val();
             var port = $('#port').val();
             var encod = $('#encod').val();
             var user = $('#username').val();
             var pwd = $('#pwd').val();
             var form1_data = {"host":host,"db":db,"port":port,"encod":encod,"user":user,"pwd":pwd};
             $.ajax({
                  type:'post',
                  url:'/con_sql',
                  data:form1_data,
                  dataType:'json',
                  success:function(data){
                        var state = data['state'];
                        if(state=='t'){
                            location.href="/import_sql";
                            alert('数据库连接成功。');
                        }
                        else{
                            alert('数据库连接失败！请仔细检查连接信息。');
                        };
                  },
                  error:function () {
                        alert('error');
                  }
              })

        });

        //删除数据库连接
        var delda = '';
        $('.del_t').click(function () {
            delda = $(this).attr('host');
            delda = {'delda':delda};
        });
        $('#del_col').click(function () {
            //$('.card-body').hide();
            $.ajax({
                type:'post',
                url:'/del_con',
                data:delda ,
                dataType:'json',
                success:function (data) {
                   if(data['mes']=='t'){alert('删除成功！');}
                   else{alert('删除失败！');}
                },
                error:function(){
                    alert('error');
                }
            })
        });


        //银行流水分析
        $('#analysis').click(function () {
            var fields = $('#keep-order').val();
            console.log(Object.keys(fields).length);
           if(Object.keys(fields).length<7){
               alert('字段位数不够，请选中7个必填字段。');
               return;
           };
           console.log($('#keep-order').val());
           var analysis_field = {};
           analysis_field['table_name'] = $('#table_name').val();
           analysis_field['main_name'] = $('#keep-order').val()[0];
           analysis_field['main_card'] = $('#keep-order').val()[1];
           analysis_field['to_name'] = $('#keep-order').val()[2];
           analysis_field['to_card'] = $('#keep-order').val()[3];
           analysis_field['sign'] = $('#keep-order').val()[5];
           analysis_field['money'] = $('#keep-order').val()[4];
           analysis_field['abstract'] = $('#keep-order').val()[6];
           console.log(analysis_field);
           $.ajax({
               type:'post',
               url:'/analysis',
               data:analysis_field,
               dataType:'json',
               success:function(res){
                   alert('正在分析请稍后！');
                   console.log(res);
                   if(res['state']=='0'){
                       alert('字段错误！');
                       return;
                   };
                   $('.table_clear').html('');
                   var res_data = res['analysis_res_data'];
                   var h = '<thead><tr>';
                  Object.keys(res_data[0]).forEach(function(item){h+='<th>'+item+'</th>';})
                  h+='</tr></thead>';
                  $('.sql_table').append(h);

                  var b = '<tbody>'
                  res_data.forEach(function (item) {
                      var h1 = '<tr>';
                      Object.values(item).forEach(function (item) {
                          h1+='<td>'+item+'</td>';
                      })
                      h1+='</tr>';
                      b+=h1;
                  })
                  b+='</tbody>';
                  $('.sql_table').append(b);
                  $('.table thead tr th').css({"color":"white"});
                  $('.table thead tr th').css({"white-space":"nowrap"});
                  $('.table thead tr th').css({"background-color":"#3d405c"});
               },
               error:function () {
                   alert('error');
               }
           });
        });
})