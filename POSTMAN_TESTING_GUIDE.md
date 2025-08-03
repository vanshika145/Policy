# 🚀 Postman Testing Guide for Policy Analysis API

## 📋 **How to Import the Collection**

1. **Open Postman**
2. **Click "Import"** (top left)
3. **Select "File"** tab
4. **Choose** `postman_collection.json`
5. **Click "Import"**

## 🎯 **Testing Order (Recommended)**

### **Step 1: Basic Connectivity Tests**
Start with these simple tests to verify the service is working:

#### **1. Health Check**
- **Method**: GET
- **URL**: `https://policy-2.onrender.com/health`
- **Expected**: `200 OK` with `{"status":"healthy","timestamp":"..."}`

#### **2. Ping**
- **Method**: GET  
- **URL**: `https://policy-2.onrender.com/ping`
- **Expected**: `200 OK` with `{"status":"pong","timestamp":"..."}`

### **Step 2: Simple Endpoint Tests**

#### **3. Hackrx Test**
- **Method**: POST
- **URL**: `https://policy-2.onrender.com/hackrx/test`
- **Headers**: `Content-Type: application/json`
- **Body**: `{"test": true}`
- **Expected**: `200 OK` with success message

#### **4. Hackrx Echo**
- **Method**: POST
- **URL**: `https://policy-2.onrender.com/hackrx/echo`
- **Headers**: `Content-Type: application/json`
- **Body**: `{"message": "Hello World", "timestamp": "2024-01-01T00:00:00Z"}`
- **Expected**: `200 OK` with echoed data

### **Step 3: Diagnostic Tests**

#### **5. Debug Pinecone**
- **Method**: GET
- **URL**: `https://policy-2.onrender.com/debug/pinecone`
- **Expected**: `200 OK` with environment status

#### **6. Hackrx Diagnose**
- **Method**: POST
- **URL**: `https://policy-2.onrender.com/hackrx/diagnose`
- **Headers**: `Content-Type: application/json`
- **Body**: `{"questions": ["What is the main topic?"], "documents": ""}`
- **Expected**: `200 OK` with diagnostic info

### **Step 4: Core Functionality Tests**

#### **7. Query Simple**
- **Method**: POST
- **URL**: `https://policy-2.onrender.com/query-simple`
- **Headers**: `Content-Type: application/json`
- **Body**: `{"query": "What is the main topic?", "k": 5}`
- **Expected**: `200 OK` with search results

#### **8. Hackrx Run Simple**
- **Method**: POST
- **URL**: `https://policy-2.onrender.com/hackrx/run-simple`
- **Headers**: `Content-Type: application/json`
- **Body**: `{"questions": ["What is the main topic?", "What are the key points?"], "documents": ""}`
- **Expected**: `200 OK` with processed answers

### **Step 5: File Upload Tests**

#### **9. Upload File Simple V2**
- **Method**: POST
- **URL**: `https://policy-2.onrender.com/upload-simple-v2`
- **Body**: `form-data`
  - **Key**: `file`
  - **Type**: File
  - **Value**: Select a PDF file
- **Expected**: `200 OK` with upload confirmation

#### **10. Hackrx Run With File**
- **Method**: POST
- **URL**: `https://policy-2.onrender.com/hackrx/run-with-file`
- **Body**: `form-data`
  - **Key**: `file`, **Type**: File, **Value**: Select a PDF file
  - **Key**: `questions`, **Type**: Text, **Value**: `["What is the main topic?", "What are the key points?"]`
- **Expected**: `200 OK` with processed answers

## 🔍 **Expected Responses**

### **✅ Success Responses (200 OK)**
```json
{
  "status": "success",
  "message": "Operation completed successfully",
  "data": {...}
}
```

### **❌ Error Responses (4xx/5xx)**
```json
{
  "detail": "Error message",
  "status_code": 400
}
```

## 🚨 **Common Issues & Solutions**

### **Issue 1: Service Not Responding**
- **Symptom**: Connection timeout or refused
- **Solution**: Check if service is deployed on Render

### **Issue 2: 502 Bad Gateway**
- **Symptom**: 502 error responses
- **Solution**: Service is down - check Render logs

### **Issue 3: Environment Variables Missing**
- **Symptom**: Pinecone or OpenAI errors
- **Solution**: Check environment variables in Render dashboard

### **Issue 4: File Upload Fails**
- **Symptom**: Upload endpoint returns error
- **Solution**: Check file size and format (PDF only)

## 📊 **Testing Checklist**

- [ ] Health check responds
- [ ] Ping responds  
- [ ] Test endpoint works
- [ ] Echo endpoint works
- [ ] Debug pinecone shows environment status
- [ ] Diagnose endpoint provides info
- [ ] Query simple returns results
- [ ] Run simple processes questions
- [ ] File upload works
- [ ] File processing works

## 🎯 **Success Criteria**

Your API is **working properly** if:
1. ✅ All basic endpoints respond (200 OK)
2. ✅ File uploads work
3. ✅ Question processing works
4. ✅ No 502 errors
5. ✅ Environment variables are set correctly

## 📞 **If Tests Fail**

1. **Check Render dashboard** for deployment status
2. **Review build logs** for errors
3. **Verify environment variables** are set
4. **Wait for deployment** to complete
5. **Retry tests** after deployment

---

**Happy Testing! 🚀** 