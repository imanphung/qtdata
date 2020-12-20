function createWorkSpace(dbsheet, tempsheet, wtsheet, dbnamelist, wtnamelist) {    
  for (var ii in dbnamelist) {
    //Get information of member
    var info = getMemberInfo(dbsheet, dbnamelist[ii]);
    try {
      var status = info[5];
    } catch (e) {
      Logger.log(ii, dbnamelist[ii])
      console.error(e);
      Browser.msgBox('Error at row [' + ii + ' - ' + dbnamelist[ii] + '] .');
      break;
    }

    if (wtnamelist.indexOf(dbnamelist[ii]) == -1) {
      var lastcol = wtsheet.getLastColumn();
      //Create new workspace if not exist
      wtsheet.insertColumnsAfter(lastcol, 11);
      //Copy template workspace
      var sourcevalue = tempsheet.getRange("B1:L4").getValues();
      var workspace = wtsheet.getRange(1,lastcol+1,sourcevalue.length,sourcevalue[0].length);
      workspace.setValues(sourcevalue);
      
      //Display information
      wtsheet.getRange(1, lastcol+1, 1, sourcevalue[0].length).merge().setBackgroundRGB(Math.random()*255, Math.random()*255, Math.random()*255); //Background format for Name
      wtsheet.getRange(1, lastcol+1).setFontColor("white").setFontSize(18).setFontWeight("bold"); //Font format for Name
      wtsheet.getRange(1, lastcol+1).setValue(info[0]); //Name
      wtsheet.getRange(3, lastcol+1).setValue(info[1]); //Email
      wtsheet.getRange(3, lastcol+2).setValue(info[2]); //Alias
      wtsheet.getRange(3, lastcol+3).setValue(info[3]); //Title
      wtsheet.getRange(3, lastcol+4).setValue(info[4]); //State
      wtsheet.getRange(3, lastcol+5).setValue(info[5]); //Status
      wtsheet.getRange(3, lastcol+6).setValue(info[7]); //Facebook
      wtsheet.getRange(3, lastcol+7).setValue(info[8]); //Phone
      wtsheet.getRange(3, lastcol+8).setValue(info[9]); //Skype
      wtsheet.getRange(3, lastcol+9).setValue(info[10]); //Hangout
      
      //Copy formula of HR
      var sourceformula1 = tempsheet.getRange("J5").getFormulaR1C1();
      var sourceformula2 = tempsheet.getRange("L5").getFormulaR1C1();
      var lastrow = wtsheet.getLastRow();
      wtsheet.getRange(5,lastcol+9, lastrow-5).setFormulaR1C1(sourceformula1);
      wtsheet.getRange(5,lastcol+11, lastrow-5).setFormulaR1C1(sourceformula2);
      wtsheet.getRange(lastrow,lastcol+9).setFormulaR1C1("=SUM(R[-"+ (lastrow-5) +"]C[0]:R[-1]C[0])");
      wtsheet.getRange(lastrow,lastcol+11).setFormulaR1C1("=SUM(R[-"+ (lastrow-5) +"]C[0]:R[-1]C[0])");
      
      //Auto resize columns to fit to data
//      wtsheet.autoResizeColumns(lastcol+1, 8);
      //Edit columns' width
      wtsheet.setColumnWidths(lastcol+1, 2, 200);
      wtsheet.setColumnWidths(lastcol+3, 6, 40);
    }
  }
}